from fastapi import APIRouter, Depends, Query, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_github_login
from app.database.session import get_db
from app.schemas.performance import StatsSummary, TimeseriesResponse
from app.services.performance_queries import get_review_timeseries, get_stats_summary
from app.services.response_cache import response_cache

router = APIRouter(prefix="/api/v1/stats", tags=["Stats"])


@router.get("/summary", response_model=StatsSummary)
async def stats_summary(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
    github_login: str = Depends(get_github_login),
):
    cache = request.app.state.response_cache
    data, cache_status = await cache.get_or_set(
        github_login,
        "stats:summary",
        lambda: get_stats_summary(db, github_login),
    )
    response.headers["X-Cache"] = cache_status
    return data


@router.get("/timeseries", response_model=TimeseriesResponse)
async def stats_timeseries(
    request: Request,
    response: Response,
    days: int = Query(default=30, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
    github_login: str = Depends(get_github_login),
):
    cache = request.app.state.response_cache
    items, cache_status = await cache.get_or_set(
        github_login,
        f"stats:timeseries:days={days}",
        lambda: get_review_timeseries(db, github_login, days),
    )
    response.headers["X-Cache"] = cache_status
    return {"items": items}
