from app.clients.github_client import GitHubClient
from app.core.config import settings


class GitHubService:

    def __init__(self):
        self.client = GitHubClient()
        self.github_token = settings.GITHUB_TOKEN
        
    async def get_repositories(self):
        return await self.client.get_repositories()

    async def fetch_pr(
        self,
        owner: str,
        repo: str,
        number: int,
    ):
        pr = await self.client.get_pull_request(
            owner,
            repo,
            number,
        )

        files = await self.client.get_pull_request_files(
            owner,
            repo,
            number,
        )

        return {
            "title": pr["title"],
            "author": pr["user"]["login"],
            "state": pr["state"],
            "files": files,
        }

    async def get_pull_request_files(
        self,
        owner: str,
        repo: str,
        pull_number: int,
    ):
        return await self.client.get_pull_request_files(
            owner,
            repo,
            pull_number,
        )

    async def create_review(
        self,
        owner: str,
        repo: str,
        pull_number: int,
        body: str,
        comments: list | None = None,
    ):
        """
        Creates a GitHub Pull Request review.

        body:
            Overall AI review summary.

        comments:
            Optional inline review comments.
            
        """
        
        async def get_repositories(self):
            return await self.client.get_repositories()

        return await self.client.create_pull_request_review(
            owner=owner,
            repo=repo,
            pull_number=pull_number,
            body=body,
            comments=comments,
        )