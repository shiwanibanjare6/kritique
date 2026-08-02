from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.repositories.repository_repository import RepositoryRepository

router = APIRouter(
    prefix="/api/v1/github",
    tags=["github"],
)


@router.get("/repositories")
async def list_repositories(
    db: AsyncSession = Depends(get_db),
):
    repo = RepositoryRepository(db)

    repositories = await repo.get_all()

    return [
        {
            "id": repository.id,
            "github_id": repository.github_id,
            "owner": repository.owner,
            "name": repository.name,
            "full_name": repository.full_name,
            "default_branch": repository.default_branch,
        }
        for repository in repositories
    ]


@router.get("/repositories/{repository_id}")
async def get_repository(
    repository_id: int,
    db: AsyncSession = Depends(get_db),
):
    repo = RepositoryRepository(db)

    repository = await repo.get_by_id(repository_id)

    if repository is None:
        raise HTTPException(
            status_code=404,
            detail="Repository not found",
        )

    total_pull_requests = len(repository.pull_requests)

    reviewed_pull_requests = sum(
        1
        for pr in repository.pull_requests
        if pr.reviews
    )

    scores = [
        max(pr.reviews, key=lambda r: r.created_at).final_score
        for pr in repository.pull_requests
        if pr.reviews
    ]

    average_score = (
        round(sum(scores) / len(scores))
        if scores
        else 0
    )

    return {
    "id": repository.id,
    "github_id": repository.github_id,
    "owner": repository.owner,
    "name": repository.name,
    "full_name": repository.full_name,
    "default_branch": repository.default_branch,

    "total_pull_requests": len(repository.pull_requests),

    "reviewed_pull_requests": sum(
        1 for pr in repository.pull_requests
        if pr.reviews
    ),

    "average_score": (
        round(
            sum(
                max(pr.reviews, key=lambda r: r.created_at).final_score
                for pr in repository.pull_requests
                if pr.reviews
            )
            /
            sum(
                1
                for pr in repository.pull_requests
                if pr.reviews
            )
        )
        if any(pr.reviews for pr in repository.pull_requests)
        else 0
    ),

    "latest_pull_requests": [
        {
            "id": pr.id,
            "pr_number": pr.pr_number,
            "title": pr.title,
            "author": pr.author,
            "state": pr.state,
        }
        for pr in sorted(
            repository.pull_requests,
            key=lambda p: p.id,
            reverse=True,
        )[:5]
    ],
}