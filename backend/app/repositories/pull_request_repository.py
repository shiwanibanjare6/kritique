from sqlalchemy import desc
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.pull_request import PullRequest


class PullRequestRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_github_id(self, github_pr_id: int):
        result = await self.db.execute(
            select(PullRequest).where(
                PullRequest.github_pr_id == github_pr_id
            )
        )

        return result.scalar_one_or_none()

    async def create(self, **kwargs):
        pr = PullRequest(**kwargs)

        self.db.add(pr)

        await self.db.commit()

        await self.db.refresh(pr)

        return pr

    async def get_all(self):
        result = await self.db.execute(
            select(PullRequest)
            .options(
                selectinload(PullRequest.repository),
                selectinload(PullRequest.reviews),
            )
            .order_by(desc(PullRequest.updated_at))
        )

        return result.scalars().all()

    async def get_by_id(self, pr_id: int):
        result = await self.db.execute(
            select(PullRequest)
            .options(
                selectinload(PullRequest.repository),
                selectinload(PullRequest.reviews),
            )
            .where(PullRequest.id == pr_id)
        )

        return result.scalar_one_or_none()