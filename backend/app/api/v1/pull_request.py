from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.repositories.pull_request_repository import PullRequestRepository


router = APIRouter(
    prefix="/api/v1/pull-requests",
    tags=["Pull Requests"],
)


@router.get("/")
async def get_pull_requests(
    db: AsyncSession = Depends(get_db),
):
    repo = PullRequestRepository(db)

    pull_requests = await repo.get_all()

    response = []

    for pr in pull_requests:

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
            }
        )

    return response


@router.get("/{pr_id}")
async def get_pull_request(
    pr_id: int,
    db: AsyncSession = Depends(get_db),
):
    repo = PullRequestRepository(db)

    pr = await repo.get_by_id(pr_id)

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
    }