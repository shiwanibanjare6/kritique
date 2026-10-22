from contextlib import asynccontextmanager
import asyncio
from time import perf_counter

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.core.config import get_cors_origins, settings
from app.core.logging import logger
from app.database.session import AsyncSessionLocal
from app.core.redis import RedisError, create_redis_client
from app.api.v1.webhook import router as webhook_router
from app.api.v1.review import router as review_router
from app.api.v1.pull_request import router as pull_request_router
from app.api.github import router as github_router
from app.api.v1.stats import router as stats_router
from app.middleware.request_logger import RequestLoggerMiddleware
from app.services.response_cache import response_cache

@asynccontextmanager
async def lifespan(app: FastAPI):
    startup_started = perf_counter()
    app.state.response_cache = response_cache
    response_cache.redis = None
    redis_started = perf_counter()
    app.state.redis = create_redis_client()
    logger.info("Startup phase=redis_client_create duration_ms=%.2f", (perf_counter() - redis_started) * 1000)
    if app.state.redis is None:
        logger.warning("REDIS_URL is empty; webhook jobs will be recovered from PostgreSQL by the worker")
    else:
        redis_ping_started = perf_counter()
        try:
            await asyncio.wait_for(app.state.redis.ping(), timeout=2)
            response_cache.redis = app.state.redis
            logger.info("Redis Ready")
        except RedisError as error:
            logger.warning("Redis unavailable at startup (%s); webhook jobs remain durable in PostgreSQL", type(error).__name__)
        except TimeoutError:
            logger.warning("Redis startup ping timed out; continuing without Redis response caching")
        finally:
            logger.info("Startup phase=redis_ping duration_ms=%.2f", (perf_counter() - redis_ping_started) * 1000)

    logger.info("Startup complete duration_ms=%.2f", (perf_counter() - startup_started) * 1000)

    yield

    shutdown_started = perf_counter()
    if app.state.redis is not None:
        await app.state.redis.aclose()
    logger.info("Application shutdown duration_ms=%.2f", (perf_counter() - shutdown_started) * 1000)


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

@app.get("/health")
async def health():
    return {
        "status": "ok"
    }


@app.get("/health/ready")
async def health_ready():
    try:
        async with asyncio.timeout(2):
            async with AsyncSessionLocal() as db:
                await db.execute(text("SELECT 1"))
    except TimeoutError as error:
        raise HTTPException(status_code=503, detail="Database readiness check timed out") from error
    except Exception as error:
        logger.warning("Database readiness check failed (%s)", type(error).__name__)
        raise HTTPException(status_code=503, detail="Database is not ready") from error
    return {"status": "ready"}

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RequestLoggerMiddleware)

# Register routers AFTER creating app
app.include_router(webhook_router)
app.include_router(review_router)
app.include_router(pull_request_router)
app.include_router(github_router)
app.include_router(stats_router)


@app.get("/")
async def root():
    return {
        "application": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "Running",
    }
