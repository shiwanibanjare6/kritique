from typing import Any

try:
    from redis.asyncio import Redis as RedisClient
    from redis.exceptions import RedisError
except ImportError:  # Keep API imports available before local dependencies are installed.
    RedisClient = None

    class RedisError(Exception):
        pass

Redis = Any

from app.core.config import settings

REVIEW_QUEUE_KEY = "kritique:review-jobs"


def create_redis_client() -> Redis | None:
    redis_url = settings.REDIS_URL.strip()
    if not redis_url or RedisClient is None:
        return None
    return RedisClient.from_url(redis_url, decode_responses=True)
