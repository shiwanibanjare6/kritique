from sqlalchemy import desc
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.review import Review


class ReviewRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, **kwargs):
        review = Review(**kwargs)

        self.db.add(review)

        await self.db.commit()

        await self.db.refresh(review)

        return review

    async def get_all(self):
        result = await self.db.execute(
            select(Review).order_by(desc(Review.created_at))
        )
        return result.scalars().all()

    async def get_by_id(self, review_id: int):
        result = await self.db.execute(
            select(Review).where(
                Review.id == review_id
            )
        )
        return result.scalar_one_or_none()

    async def get_by_pull_request(self, pull_request_id: int):
        result = await self.db.execute(
            select(Review)
            .where(
                Review.pull_request_id == pull_request_id
            )
            .order_by(desc(Review.created_at))
        )

        return result.scalars().all()