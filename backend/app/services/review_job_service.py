import re
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.core.config import settings
from app.core.logging import logger
from app.database.session import AsyncSessionLocal
from app.models.pull_request import PullRequest
from app.models.pull_request_file import PullRequestFile
from app.models.review import Review
from app.models.review_job import ReviewJob
from app.services.ai_review_service import AIReviewService
from app.services.github_service import GitHubService
from app.services.response_cache import response_cache


def _safe_error_message(error: Exception) -> str:
    message = f"{type(error).__name__}: {error}"
    for secret in (settings.GITHUB_TOKEN, settings.GITHUB_SECRET, settings.GROQ_API_KEY, settings.DATABASE_URL):
        if secret:
            message = message.replace(secret, "[REDACTED]")
    message = re.sub(r"(?i)Bearer\s+\S+", "Bearer [REDACTED]", message)
    message = re.sub(
        r"(?i)(api[_ -]?key|authorization|password|token)(\s*[:=]\s*)[^\s,;]+",
        r"\1\2[REDACTED]",
        message,
    )
    message = re.sub(r"(?i)\b(?:gh[pousr]_[A-Za-z0-9_]{20,}|gsk_[A-Za-z0-9_]{20,})\b", "[REDACTED]", message)
    message = re.sub(r"(?i)(https?://)[^/@\s:]+:[^/@\s]+@", r"\1[REDACTED]@", message)
    return message[:1000]


async def execute_review_job(
    job_id: int,
    session_factory: async_sessionmaker = AsyncSessionLocal,
) -> bool:
    """Claim and execute one durable review job; failures are recorded and returned."""
    async with session_factory() as db:
        result = await db.execute(
            select(ReviewJob)
            .where(ReviewJob.id == job_id)
            .with_for_update(skip_locked=True)
        )
        job = result.scalar_one_or_none()
        if job is None or job.status != "queued":
            return False

        job.status = "processing"
        job.started_at = datetime.now(UTC).replace(tzinfo=None)
        job.completed_at = None
        job.error_message = None
        job.attempt_count += 1
        await db.commit()

    ai_client = None
    try:
        async with session_factory() as db:
            result = await db.execute(
                select(ReviewJob)
                .options(selectinload(ReviewJob.pull_request).selectinload(PullRequest.repository))
                .where(ReviewJob.id == job_id)
            )
            job = result.scalar_one()
            pull_request = job.pull_request
            repository = pull_request.repository
            pr_id = pull_request.id
            pr_number = pull_request.pr_number
            repository_owner = repository.owner
            repository_name = repository.name
            repository_full_name = repository.full_name

        logger.info(
            "Review job %s started for %s#%s",
            job_id,
            repository_full_name,
            pr_number,
        )

        github_service = GitHubService()
        ai_review = AIReviewService()
        ai_client = getattr(ai_review, "client", None)
        files = await github_service.get_pull_request_files(
            repository_owner,
            repository_name,
            pr_number,
        )

        pr_summaries: list[str] = []
        review_scores = {
            "security_score": 0.0,
            "style_score": 0.0,
            "architecture_score": 0.0,
            "final_score": 0.0,
        }
        all_comments: list[dict[str, Any]] = []
        all_agent_output: list[dict[str, Any]] = []
        pull_request_files: list[PullRequestFile] = []

        for file in files:
            patch = file.get("patch")
            review = await ai_review.review_code(
                filename=file["filename"],
                patch=patch or "",
            )
            pull_request_files.append(
                PullRequestFile(
                    pull_request_id=pr_id,
                    filename=file["filename"],
                    status=file["status"],
                    additions=file["additions"],
                    deletions=file["deletions"],
                    changes=file["changes"],
                    patch=patch,
                )
            )
            all_agent_output.append({"file": file["filename"], "review": review})
            pr_summaries.append(
                f"File: {file['filename']}\n\nSummary:\n{review['summary']}\n\n"
                f"Security Score: {review['security_score']}\n"
                f"Style Score: {review['style_score']}\n"
                f"Architecture Score: {review['architecture_score']}\n"
                f"Overall Score: {review['final_score']}"
            )
            for score_name in review_scores:
                review_scores[score_name] += review.get(score_name, 0)
            for comment in review.get("comments", []):
                all_comments.append(
                    {
                        "path": file["filename"],
                        "line": comment["line"],
                        "side": "RIGHT",
                        "body": (
                            f"**{comment['severity'].upper()}**\n\n"
                            f"{comment['comment']}"
                        ),
                    }
                )

        overall_review = await ai_review.review_pull_request(pr_summaries)
        file_count = max(len(files), 1)
        scores = {name: value / file_count for name, value in review_scores.items()}

        async with session_factory() as db:
            for file in await db.scalars(
                select(PullRequestFile).where(PullRequestFile.pull_request_id == pr_id)
            ):
                await db.delete(file)
            db.add_all(pull_request_files)
            db.add(
                Review(
                    pull_request_id=pr_id,
                    summary=overall_review["summary"],
                    security_score=scores["security_score"],
                    style_score=scores["style_score"],
                    architecture_score=scores["architecture_score"],
                    final_score=scores["final_score"],
                    merge_recommendation=overall_review["merge_recommendation"],
                    risk_level=overall_review["risk_level"],
                    strengths=overall_review["strengths"],
                    weaknesses=overall_review["weaknesses"],
                    agent_output=all_agent_output,
                )
            )
            await db.commit()

        await response_cache.invalidate_all()

        await github_service.create_review(
            owner=repository_owner,
            repo=repository_name,
            pull_number=pr_number,
            body=(
                f"## 🤖 AI Review Summary\n\n{overall_review['summary']}\n\n"
                f"### Risk Level\n{overall_review['risk_level']}\n\n"
                f"### Merge Recommendation\n{overall_review['merge_recommendation']}\n\n"
                "### Strengths\n"
                + "\n".join(f"- {item}" for item in overall_review["strengths"])
                + "\n\n### Weaknesses\n"
                + "\n".join(f"- {item}" for item in overall_review["weaknesses"])
            ),
            comments=all_comments if all_comments else None,
        )

        async with session_factory() as db:
            job = await db.scalar(select(ReviewJob).where(ReviewJob.id == job_id))
            job.status = "completed"
            job.completed_at = datetime.now(UTC).replace(tzinfo=None)
            job.error_message = None
            await db.commit()
        logger.info(
            "Review job %s completed for %s#%s (%s files)",
            job_id,
            repository_full_name,
            pr_number,
            len(files),
        )
        return True
    except Exception as error:
        safe_message = _safe_error_message(error)
        async with session_factory() as db:
            result = await db.execute(select(ReviewJob).where(ReviewJob.id == job_id))
            job = result.scalar_one_or_none()
            if job is not None:
                job.status = "failed"
                job.completed_at = datetime.now(UTC).replace(tzinfo=None)
                job.error_message = safe_message
                await db.commit()
                logger.error(
                    "Review job %s failed for repository %s PR %s (%s)",
                    job.id,
                    job.repository_id,
                    job.pull_request_id,
                    type(error).__name__,
                )
        return False
    finally:
        if ai_client is not None:
            try:
                await ai_client.close()
            except Exception:
                logger.warning("Unable to close AI client after review job %s", job_id)
