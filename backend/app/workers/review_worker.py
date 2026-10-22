import asyncio
from datetime import UTC, datetime

from sqlalchemy import select, update

from app.core.logging import logger
from app.core.redis import RedisError, REVIEW_QUEUE_KEY, create_redis_client
from app.database.session import AsyncSessionLocal
from app.models.review_job import ReviewJob
from app.services.review_job_service import _safe_error_message, execute_review_job
from app.services.response_cache import response_cache


async def _next_durable_job_id() -> int | None:
    async with AsyncSessionLocal() as db:
        return await db.scalar(
            select(ReviewJob.id)
            .where(ReviewJob.status == "queued")
            .order_by(ReviewJob.created_at, ReviewJob.id)
            .limit(1)
        )


async def _mark_interrupted_jobs_failed() -> None:
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            update(ReviewJob)
            .where(ReviewJob.status == "processing")
            .values(
                status="failed",
                completed_at=datetime.now(UTC).replace(tzinfo=None),
                error_message="Worker restarted while processing. A new pull-request event can retry this revision.",
            )
        )
        await db.commit()
        if result.rowcount:
            logger.warning("Marked %s interrupted review jobs as failed", result.rowcount)


async def process_review_job_message(job_id: int) -> None:
    """Keep one job error from terminating the worker's main loop."""
    try:
        await execute_review_job(job_id)
    except Exception as error:
        logger.error("Review job %s could not be claimed (%s)", job_id, _safe_error_message(error))


async def run_worker() -> None:
    await _mark_interrupted_jobs_failed()
    redis = create_redis_client()
    response_cache.redis = redis
    try:
        while True:
            try:
                queued = await _next_durable_job_id()
                if queued is not None:
                    await process_review_job_message(queued)
                    continue

                if redis is None:
                    await asyncio.sleep(3)
                    continue
                message = await redis.blpop(REVIEW_QUEUE_KEY, timeout=3)
                if message is not None:
                    try:
                        job_id = int(message[1])
                    except (TypeError, ValueError):
                        logger.warning("Discarded malformed review queue entry")
                        continue
                    await process_review_job_message(job_id)
            except RedisError as error:
                # PostgreSQL is authoritative: poll it even when Redis is down.
                logger.warning("Redis unavailable in review worker (%s)", type(error).__name__)
                await asyncio.sleep(3)
            except Exception as error:
                logger.error("Review worker iteration failed (%s)", type(error).__name__)
                await asyncio.sleep(1)
    finally:
        if redis is not None:
            await redis.aclose()


if __name__ == "__main__":
    asyncio.run(run_worker())
