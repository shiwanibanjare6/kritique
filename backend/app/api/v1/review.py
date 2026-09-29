from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.repositories.review_repository import ReviewRepository
from app.api.dependencies import get_github_login

router = APIRouter(
    prefix="/api/v1/reviews",
    tags=["Reviews"],
)


@router.get("/")
async def get_all_reviews(
    db: AsyncSession = Depends(get_db),
    github_login: str = Depends(get_github_login),
):
    repo = ReviewRepository(db)

    reviews = await repo.get_all_for_user(github_login)

    return reviews


@router.get("/{review_id}")
async def get_review(
    review_id: int,
    db: AsyncSession = Depends(get_db),
    github_login: str = Depends(get_github_login),
):
    repo = ReviewRepository(db)

    review = await repo.get_by_id(review_id)

    if review is None:
        raise HTTPException(
            status_code=404,
            detail="Review not found",
        )

    if not await repo.is_owned_by_user(review_id, github_login):
        raise HTTPException(status_code=404, detail="Review not found")

    return review


@router.get("/pull-request/{pull_request_id}")
async def get_pull_request_reviews(
    pull_request_id: int,
    db: AsyncSession = Depends(get_db),
    github_login: str = Depends(get_github_login),
):
    repo = ReviewRepository(db)

    if not await repo.pull_request_is_owned_by_user(pull_request_id, github_login):
        raise HTTPException(status_code=404, detail="Pull Request not found")
    reviews = await repo.get_by_pull_request(pull_request_id)

    return reviews
