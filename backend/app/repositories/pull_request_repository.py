from sqlalchemy import desc
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.pull_request import PullRequest
from app.models.repository_connection import RepositoryConnection


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

    async def sync_from_github(self, repository_id: int, github_pull_requests: list[dict]):
        for item in github_pull_requests:
            pr = await self.get_by_github_id(item["id"])
            values = {
                "repository_id": repository_id,
                "github_pr_id": item["id"],
                "html_url": item["html_url"],
                "pr_number": item["number"],
                "title": item["title"],
                "author": item["user"]["login"],
                "state": item["state"],
                "base_branch": item["base"]["ref"],
                "head_branch": item["head"]["ref"],
            }
            if pr is None:
                self.db.add(PullRequest(**values))
            elif pr.repository_id == repository_id:
                for field, value in values.items():
                    setattr(pr, field, value)

        await self.db.commit()

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

    async def get_all_for_user(self, github_login: str):
        result = await self.db.execute(
            select(PullRequest)
            .join(RepositoryConnection, PullRequest.repository_id == RepositoryConnection.repository_id)
            .options(selectinload(PullRequest.repository), selectinload(PullRequest.reviews))
            .where(RepositoryConnection.github_login == github_login)
            .order_by(desc(PullRequest.updated_at))
        )
        return result.scalars().unique().all()

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

    async def get_by_id_for_user(self, pr_id: int, github_login: str):
        result = await self.db.execute(
            select(PullRequest)
            .join(RepositoryConnection, PullRequest.repository_id == RepositoryConnection.repository_id)
            .options(selectinload(PullRequest.repository), selectinload(PullRequest.reviews))
            .where(PullRequest.id == pr_id, RepositoryConnection.github_login == github_login)
        )
        return result.scalar_one_or_none()
