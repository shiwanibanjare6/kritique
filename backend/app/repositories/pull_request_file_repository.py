from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.pull_request_file import PullRequestFile


class PullRequestFileRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        pull_request_id: int,
        filename: str,
        status: str,
        additions: int,
        deletions: int,
        changes: int,
        patch: str | None,
    ) -> PullRequestFile:

        file = PullRequestFile(
            pull_request_id=pull_request_id,
            filename=filename,
            status=status,
            additions=additions,
            deletions=deletions,
            changes=changes,
            patch=patch,
        )

        self.db.add(file)
        await self.db.commit()
        await self.db.refresh(file)

        return file

    async def get_by_pr(self, pull_request_id: int):
        result = await self.db.execute(
            select(PullRequestFile).where(
                PullRequestFile.pull_request_id == pull_request_id
            )
        )

        return result.scalars().all()

    async def delete_by_pr(self, pull_request_id: int):

        files = await self.get_by_pr(pull_request_id)

        for file in files:
            await self.db.delete(file)

        await self.db.commit()