from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.pull_request import PullRequest
from app.models.repository import Repository
from app.models.repository_connection import RepositoryConnection


class RepositoryRepository:

    def __init__(self, db: AsyncSession):
        self.db = db
        
    async def get_all(self):
        result = await self.db.execute(
            select(Repository).order_by(Repository.name)
        )
        return result.scalars().all()

    async def get_all_for_user(self, github_login: str):
        result = await self.db.execute(
            select(Repository)
            .join(RepositoryConnection)
            .where(RepositoryConnection.github_login == github_login)
            .order_by(Repository.name)
        )
        return result.scalars().all()

    async def is_connected_to_user(self, repository_id: int, github_login: str) -> bool:
        result = await self.db.execute(
            select(RepositoryConnection.repository_id).where(
                RepositoryConnection.repository_id == repository_id,
                RepositoryConnection.github_login == github_login,
            )
        )
        return result.scalar_one_or_none() is not None

    async def connect_to_user(self, repository_id: int, github_login: str):
        if not await self.is_connected_to_user(repository_id, github_login):
            self.db.add(RepositoryConnection(repository_id=repository_id, github_login=github_login))
            await self.db.commit()

    async def get_by_github_id(self, github_id: int):
        result = await self.db.execute(
            select(Repository).where(
                Repository.github_id == github_id
            )
        )
        return result.scalar_one_or_none()
    
    async def get_by_id(self, repository_id: int):
        result = await self.db.execute(
            select(Repository)
            .options(
                selectinload(Repository.pull_requests).selectinload(
                    PullRequest.reviews
                )
            )
            .where(
                Repository.id == repository_id
            )
        )
        return result.scalar_one_or_none()
    
    async def create(
        self,
        github_id: int,
        owner: str,
        name: str,
        full_name: str,
        default_branch: str,
    ):
        
        
        repository = Repository(
            github_id=github_id,
            owner=owner,
            name=name,
            full_name=full_name,
            default_branch=default_branch,
        )

        self.db.add(repository)
        await self.db.commit()
        await self.db.refresh(repository)

        return repository
