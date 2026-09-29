from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_cors_origins, settings
from app.core.logging import logger
from app.database.init_db import init_database
from app.api.v1.webhook import router as webhook_router
from app.api.v1.review import router as review_router
from app.api.v1.pull_request import router as pull_request_router
from app.api.github import router as github_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing Database...")

    await init_database()

    logger.info("Database Ready")

    yield

    logger.info("Application Shutdown")


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

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers AFTER creating app
app.include_router(webhook_router)
app.include_router(review_router)
app.include_router(pull_request_router)
app.include_router(github_router)


@app.get("/")
async def root():
    return {
        "application": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "Running",
    }
