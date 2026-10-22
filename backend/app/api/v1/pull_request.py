from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Query
from fastapi import Request
from fastapi import Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.repositories.pull_request_repository import PullRequestRepository
from app.api.dependencies import get_github_login
from app.models.review_job import ReviewJob
from app.schemas.performance import PullRequestSummaryResponse
from app.services.performance_queries import (
    get_pull_request_summary,
    list_pull_request_rows,
    list_review_jobs,
    review_status_by_pull_request,
)


router = APIRouter(
    prefix="/api/v1/pull-requests",
    tags=["Pull Requests"],
)


@router.get("/")
async def get_pull_requests(
    db: AsyncSession = Depends(get_db),
    github_login: str = Depends(get_github_login),
):
    rows = await list_pull_request_rows(db, github_login, include_agent_output=True)
    pull_requests = [pr for pr, _review in rows]
    latest_reviews = {pr.id: review for pr, review in rows if review is not None}
    jobs = await list_review_jobs(db, [pr.id for pr in pull_requests])
    statuses = review_status_by_pull_request(pull_requests, jobs, latest_reviews)

    response = []

    for pr in pull_requests:
        latest = latest_reviews.get(pr.id)
        latest_review = None if latest is None else {
            "id": latest.id,
            "summary": latest.summary,
            "security_score": latest.security_score,
            "style_score": latest.style_score,
            "architecture_score": latest.architecture_score,
            "final_score": latest.final_score,
            "merge_recommendation": latest.merge_recommendation,
            "risk_level": latest.risk_level,
            "strengths": latest.strengths,
            "weaknesses": latest.weaknesses,
            "created_at": latest.created_at,
            "agent_output": latest.agent_output,
        }

        response.append(
            {
                "id": pr.id,
                "pr_number": pr.pr_number,
                "title": pr.title,
                "author": pr.author,
                "state": pr.state,
                "base_branch": pr.base_branch,
                "head_branch": pr.head_branch,

                "repository": {
                    "id": pr.repository.id,
                    "name": pr.repository.name,
                    "full_name": pr.repository.full_name,
                    "owner": pr.repository.owner,
                },

                "latest_review": latest_review,
                "review_status": statuses[pr.id],
            }
        )

    return response


@router.get("/summary", response_model=PullRequestSummaryResponse)
async def get_pull_requests_summary(
    request: Request,
    response: Response,
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    state: str | None = Query(default=None, max_length=30),
    q: str | None = Query(default=None, max_length=200),
    db: AsyncSession = Depends(get_db),
    github_login: str = Depends(get_github_login),
):
    cache = request.app.state.response_cache
    key = f"pull-requests:summary:{limit}:{offset}:{state or ''}:{q or ''}"
    data, cache_status = await cache.get_or_set(
        github_login,
        key,
        lambda: get_pull_request_summary(
            db,
            github_login,
            limit=limit,
            offset=offset,
            state=state,
            q=q,
        ),
    )
    response.headers["X-Cache"] = cache_status
    return data


@router.get("/{pr_id}")
async def get_pull_request(
    pr_id: int,
    db: AsyncSession = Depends(get_db),
    github_login: str = Depends(get_github_login),
):
    repo = PullRequestRepository(db)

    pr = await repo.get_by_id_for_user(pr_id, github_login)

    if pr is None:
        raise HTTPException(
            status_code=404,
            detail="Pull Request not found",
        )

    latest_review = None

    if pr.reviews:
        latest = max(
            pr.reviews,
            key=lambda r: r.created_at,
        )

        latest_review = {
            "id": latest.id,
            "summary": latest.summary,

            "security_score": latest.security_score,
            "style_score": latest.style_score,
            "architecture_score": latest.architecture_score,
            "final_score": latest.final_score,

            "merge_recommendation": latest.merge_recommendation,
            "risk_level": latest.risk_level,
            "strengths": latest.strengths,
            "weaknesses": latest.weaknesses,

            "created_at": latest.created_at,
            "agent_output": latest.agent_output,
        }

    jobs = await db.scalars(
        select(ReviewJob)
        .where(ReviewJob.pull_request_id == pr.id)
        .order_by(ReviewJob.created_at.desc())
    )

    return {
        "id": pr.id,
        "pr_number": pr.pr_number,
        "url": pr.html_url,
        "title": pr.title,
        "author": pr.author,
        "state": pr.state,
        "base_branch": pr.base_branch,
        "head_branch": pr.head_branch,

        "repository": {
            "id": pr.repository.id,
            "name": pr.repository.name,
            "full_name": pr.repository.full_name,
            "owner": pr.repository.owner,
        },

        "latest_review": latest_review,
        "review_status": _review_status(pr, jobs, latest_review),
    }


def _review_status(pr, jobs, latest_review):
    for job in jobs:
        if pr.head_sha is None or job.head_sha == pr.head_sha:
            return job.status
    return "completed" if latest_review is not None else "pending"
