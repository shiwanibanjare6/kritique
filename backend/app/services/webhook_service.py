from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import logger
from app.models.pull_request import PullRequest
from app.models.repository import Repository
from app.models.review_job import ReviewJob
from app.models.webhook_event import WebhookEvent
from app.services.review_queue import enqueue_review_job
from app.core.redis import Redis
from app.services.response_cache import response_cache


class WebhookService:
    SUPPORTED_ACTIONS = {"opened", "reopened", "synchronize", "ready_for_review"}

    def __init__(self, db: AsyncSession, redis: Redis | None = None):
        self.db = db
        self.redis = redis

    async def process_pull_request(
        self,
        payload: dict,
        event_type: str,
        delivery_id: str,
    ) -> dict:
        if event_type != "pull_request" or "pull_request" not in payload:
            return {"status": "ignored", "reason": "Unsupported GitHub event"}

        action = payload.get("action")
        if action not in self.SUPPORTED_ACTIONS:
            return {"status": "ignored", "reason": "Pull request action does not require a review"}

        repo_data = payload.get("repository") or {}
        pr_data = payload.get("pull_request") or {}
        head_data = pr_data.get("head") or {}
        owner_data = repo_data.get("owner") or {}
        user_data = pr_data.get("user") or {}
        revision_sha = head_data.get("sha")
        required = (
            repo_data.get("id"), owner_data.get("login"), repo_data.get("name"),
            repo_data.get("full_name"), repo_data.get("default_branch"),
            pr_data.get("id"), pr_data.get("number"), pr_data.get("html_url"),
            pr_data.get("title"), user_data.get("login"), pr_data.get("state"),
            (pr_data.get("base") or {}).get("ref"), head_data.get("ref"), revision_sha,
        )
        if not all(required):
            return {"status": "ignored", "reason": "Pull request payload is missing required fields"}

        # Unique database constraints arbitrate concurrent deliveries. Retry the
        # transaction so the loser can observe the durable job/event and respond safely.
        for attempt in range(3):
            try:
                existing_event = await self.db.scalar(
                    select(WebhookEvent).where(WebhookEvent.delivery_id == delivery_id)
                )
                if existing_event is not None:
                    return {"status": "duplicate", "delivery_id": delivery_id}

                repository = await self.db.scalar(
                    select(Repository).where(Repository.github_id == repo_data["id"])
                )
                if repository is None:
                    repository = Repository(
                        github_id=repo_data["id"],
                        owner=owner_data["login"],
                        name=repo_data["name"],
                        full_name=repo_data["full_name"],
                        default_branch=repo_data["default_branch"],
                    )
                    self.db.add(repository)
                    await self.db.flush()

                pull_request = await self.db.scalar(
                    select(PullRequest).where(PullRequest.github_pr_id == pr_data["id"])
                )
                current_job = None
                if pull_request is None:
                    pull_request = PullRequest(
                        repository_id=repository.id,
                        github_pr_id=pr_data["id"],
                        html_url=pr_data["html_url"],
                        pr_number=pr_data["number"],
                        title=pr_data["title"],
                        author=user_data["login"],
                        state=pr_data["state"],
                        base_branch=pr_data["base"]["ref"],
                        head_branch=head_data["ref"],
                        head_sha=revision_sha,
                    )
                    self.db.add(pull_request)
                    await self.db.flush()
                else:
                    current_job = await self.db.scalar(
                        select(ReviewJob).where(
                            ReviewJob.pull_request_id == pull_request.id,
                            ReviewJob.head_sha == revision_sha,
                        )
                    )
                    if current_job is not None:
                        self.db.add(
                            WebhookEvent(
                                repository_id=repository.id,
                                delivery_id=delivery_id,
                                event_type=event_type,
                                payload=payload,
                            )
                        )
                        await self.db.commit()
                        logger.info(
                            "Duplicate review revision ignored for %s#%s (job %s)",
                            repository.full_name,
                            pull_request.pr_number,
                            current_job.id,
                        )
                        return {"status": "duplicate", "job_id": current_job.id}

                    pull_request.html_url = pr_data["html_url"]
                    pull_request.title = pr_data["title"]
                    pull_request.author = user_data["login"]
                    pull_request.state = pr_data["state"]
                    pull_request.base_branch = pr_data["base"]["ref"]
                    pull_request.head_branch = head_data["ref"]
                    pull_request.head_sha = revision_sha

                job = ReviewJob(
                    repository_id=repository.id,
                    pull_request_id=pull_request.id,
                    head_sha=revision_sha,
                    status="queued",
                )
                self.db.add(job)

                self.db.add(
                    WebhookEvent(
                        repository_id=repository.id,
                        delivery_id=delivery_id,
                        event_type=event_type,
                        payload=payload,
                    )
                )
                await self.db.flush()
                await self.db.commit()
                await self.db.refresh(job)
                await response_cache.invalidate_all()

                logger.info(
                    "Review job %s queued for %s#%s revision %s",
                    job.id,
                    repository.full_name,
                    pull_request.pr_number,
                    revision_sha[:12],
                )
                await enqueue_review_job(self.redis, job.id)
                return {
                    "status": "queued",
                    "job_id": job.id,
                    "repository": repository.full_name,
                    "pull_request": pull_request.pr_number,
                }
            except IntegrityError:
                await self.db.rollback()
                if attempt == 2:
                    raise
                continue
            except Exception:
                await self.db.rollback()
                raise

        raise RuntimeError("Unable to persist review job")
