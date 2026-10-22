import asyncio
import hashlib
import json
import time
from collections.abc import Awaitable, Callable
from typing import Any, TypeVar

from app.core.logging import logger

T = TypeVar("T")


class TTLResponseCache:
    """Short-lived response cache; keys are always scoped to an identity."""

    def __init__(self, ttl_seconds: int = 30, redis: Any | None = None):
        self.ttl_seconds = ttl_seconds
        self.redis = redis
        self._entries: dict[str, tuple[float, Any]] = {}
        self._epoch = 0
        self._user_epochs: dict[str, int] = {}
        self._lock = asyncio.Lock()

    @staticmethod
    def _identity_key(identity: str) -> str:
        return hashlib.sha256(identity.casefold().encode("utf-8")).hexdigest()

    async def _current_epoch(self, identity: str) -> tuple[int, int]:
        user_key = self._identity_key(identity)
        if self.redis is not None:
            try:
                global_value, user_value = await self.redis.mget(
                    "kritique:api-cache:epoch",
                    f"kritique:api-cache:user-epoch:{user_key}",
                )
                return int(global_value or 0), int(user_value or 0)
            except Exception as error:
                logger.debug("Redis response-cache epoch unavailable (%s)", type(error).__name__)
        return self._epoch, self._user_epochs.get(user_key, 0)

    async def get_or_set(
        self,
        identity: str,
        endpoint_key: str,
        factory: Callable[[], Awaitable[T]],
    ) -> tuple[T, str]:
        epoch, user_epoch = await self._current_epoch(identity)
        cache_key = (
            f"kritique:api-cache:{self._identity_key(identity)}:{epoch}:{user_epoch}:{endpoint_key}"
        )

        if self.redis is not None:
            try:
                cached = await self.redis.get(cache_key)
                if cached is not None:
                    return json.loads(cached), "HIT"
            except Exception as error:
                logger.debug("Redis response-cache read unavailable (%s)", type(error).__name__)

        async with self._lock:
            local = self._entries.get(cache_key)
            if local is not None and local[0] > time.monotonic():
                return local[1], "HIT"

        value = await factory()
        encoded = json.dumps(value, separators=(",", ":"), default=str)
        serializable = json.loads(encoded)
        async with self._lock:
            self._entries[cache_key] = (time.monotonic() + self.ttl_seconds, serializable)

        if self.redis is not None:
            try:
                await self.redis.set(cache_key, encoded, ex=self.ttl_seconds)
            except Exception as error:
                logger.debug("Redis response-cache write unavailable (%s)", type(error).__name__)

        return serializable, "MISS"

    async def invalidate_user(self, identity: str) -> None:
        # Bump a shared generation so every cached response for this identity expires.
        if self.redis is not None:
            try:
                await self.redis.incr(
                    f"kritique:api-cache:user-epoch:{self._identity_key(identity)}"
                )
                return
            except Exception as error:
                logger.debug("Redis user-cache invalidation unavailable (%s)", type(error).__name__)
        identity_key = self._identity_key(identity)
        self._user_epochs[identity_key] = self._user_epochs.get(identity_key, 0) + 1

    async def invalidate_all(self) -> None:
        if self.redis is not None:
            try:
                await self.redis.incr("kritique:api-cache:epoch")
                return
            except Exception as error:
                logger.debug("Redis cache invalidation unavailable (%s)", type(error).__name__)
        self._epoch += 1


response_cache = TTLResponseCache(ttl_seconds=30)
