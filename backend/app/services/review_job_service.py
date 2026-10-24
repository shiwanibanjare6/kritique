import asyncio
import re
import time
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
from app.services.ai_review_service import AIReviewService, get_skip_reason
from app.agents.merge_agent import merge_pull_request_results
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
        ai_client = ai_review
        pipeline_started = time.perf_counter()
        files = await github_service.get_pull_request_files(
            repository_owner,
            repository_name,
            pr_number,
        )

        all_comments: list[dict[str, Any]] = []
        all_agent_output: list[dict[str, Any]] = []
        pull_request_files: list[PullRequestFile] = []

        async def review_file(file: dict) -> tuple[dict, dict, str | None, bool]:
            filename = file["filename"]
            patch = file.get("patch")
            skip_reason = get_skip_reason(filename, patch)
            if skip_reason:
                return file, {
                    "status": "skipped",
                    "summary": f"Review skipped: {skip_reason}.",
                    "reason": skip_reason,
                    "comments": [],
                    "truncated": False,
                }, None, False
            try:
                review = await ai_review.review_code(filename=filename, patch=patch)
                return file, review, None, bool(review.get("truncated", False))
            except Exception as error:
                reason = _safe_error_message(error)
                was_truncated = len(patch or "") > settings.MAX_PATCH_CHARS
                return file, {
                    "status": "failed",
                    "summary": f"Review failed: {reason}",
                    "reason": reason,
                    "comments": [],
                    "truncated": was_truncated,
                }, reason, was_truncated

        # File coroutines may overlap, but each agent request (across every file)
        # shares the single PR-scoped MAX_CONCURRENT_LLM_CALLS semaphore.
        file_results = await asyncio.gather(*(review_file(file) for file in files))
        successful_reviews: list[dict] = []
        failed_count = 0
        skipped_count = 0
        for file, review, review_error, truncated in file_results:
            status = review.get("status", "reviewed")
            if status == "reviewed":
                successful_reviews.append(review)
            elif status == "skipped":
                skipped_count += 1
            else:
                failed_count += 1
            pull_request_files.append(
                PullRequestFile(
                    pull_request_id=pr_id,
                    filename=file["filename"],
                    status=file["status"],
                    additions=file["additions"],
                    deletions=file["deletions"],
                    changes=file["changes"],
                    patch=file.get("patch"),
                    review_status=status,
                    review_error=review_error or (review.get("reason") if status == "skipped" else None),
                    truncated=truncated,
                )
            )
            all_agent_output.append({"file": file["filename"], "review": review})
            for comment in review.get("comments", []):
                if comment.get("line") is None:
                    continue
                all_comments.append({
                    "path": file["filename"],
                    "line": comment["line"],
                    "side": "RIGHT",
                    "body": f"**{comment['severity'].upper()}**\n\n{comment['comment']}",
                })

        # Store per-file failed/skipped outcomes without fabricating a Review score.
        async def replace_file_outcomes():
            async with session_factory() as db:
                for old_file in await db.scalars(
                    select(PullRequestFile).where(PullRequestFile.pull_request_id == pr_id)
                ):
                    await db.delete(old_file)
                db.add_all(pull_request_files)
                await db.commit()

        if not successful_reviews:
            await replace_file_outcomes()
            raise RuntimeError(
                f"Review job produced no successful file reviews; files_failed={failed_count}, "
                f"files_skipped={skipped_count}"
            )

        aggregate = merge_pull_request_results(successful_reviews)
        overall_review = await ai_review.review_pull_request(successful_reviews)
        # Merge decisions and numeric values are deterministic; only the prose
        # summary may come from the model or its code-built fallback.
        overall_review = {**aggregate, **overall_review, **{
            key: aggregate[key]
            for key in (
                "security_score", "style_score", "architecture_score", "final_score",
                "risk_level", "merge_recommendation", "strengths", "weaknesses",
            )
        }}
        summary_source = overall_review.get("summary_source", "fallback")
        duration_ms = round((time.perf_counter() - pipeline_started) * 1000)

        async with session_factory() as db:
            db.add(
                Review(
                    pull_request_id=pr_id,
                    summary=overall_review["summary"],
                    security_score=overall_review["security_score"],
                    style_score=overall_review["style_score"],
                    architecture_score=overall_review["architecture_score"],
                    final_score=overall_review["final_score"],
                    merge_recommendation=overall_review["merge_recommendation"],
                    risk_level=overall_review["risk_level"],
                    strengths=overall_review["strengths"],
                    weaknesses=overall_review["weaknesses"],
                    agent_output=all_agent_output,
                    pipeline_metrics=list(getattr(ai_review, "pipeline_metrics", [])),
                    duration_ms=duration_ms,
                    files_reviewed=len(successful_reviews),
                    files_skipped=skipped_count,
                    files_failed=failed_count,
                    summary_source=summary_source,
                )
            )
            db.add_all(pull_request_files)
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
        await response_cache.invalidate_all()
        return False
    finally:
        if ai_client is not None:
            try:
                close = getattr(ai_client, "close", None)
                if close is not None:
                    await close()
            except Exception:
                logger.warning("Unable to close AI client after review job %s", job_id)
