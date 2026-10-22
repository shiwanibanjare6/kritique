from app.core.logging import logger
from app.core.redis import Redis, RedisError, REVIEW_QUEUE_KEY


async def enqueue_review_job(redis: Redis | None, job_id: int) -> bool:
    if redis is None:
        logger.warning("Review job %s saved to PostgreSQL but Redis is unavailable", job_id)
        return False
    try:
        await redis.rpush(REVIEW_QUEUE_KEY, str(job_id))
        return True
    except RedisError as error:
        logger.warning(
            "Review job %s saved to PostgreSQL; Redis enqueue failed (%s)",
            job_id,
            type(error).__name__,
        )
        return False
