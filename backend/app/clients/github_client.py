import httpx

from app.core.config import settings


class GitHubClient:

    def __init__(self, token: str | None = None):
        self.base_url = "https://api.github.com"

        # Use a user token when provided.
        # Otherwise use the server-side GitHub token.
        github_token = token or settings.GITHUB_TOKEN

        self.headers = {
            "Authorization": f"Bearer {github_token}",
            "Accept": "application/vnd.github+json",
        }

    async def get_repositories(self):
        url = f"{self.base_url}/user/repos"

        async with httpx.AsyncClient() as client:
            response = await client.get(
                url,
                headers=self.headers,
                params={
                    "per_page": 100,
                    "sort": "updated",
                },
            )

        response.raise_for_status()
        return response.json()

    async def get_pull_request(
        self,
        owner: str,
        repo: str,
        number: int,
    ):
        url = f"{self.base_url}/repos/{owner}/{repo}/pulls/{number}"

        async with httpx.AsyncClient() as client:
            response = await client.get(
                url,
                headers=self.headers,
            )

        response.raise_for_status()
        return response.json()

    async def get_pull_request_files(
        self,
        owner: str,
        repo: str,
        number: int,
    ):
        url = (
            f"{self.base_url}/repos/"
            f"{owner}/{repo}/pulls/{number}/files"
        )

        async with httpx.AsyncClient() as client:
            response = await client.get(
                url,
                headers=self.headers,
            )

        response.raise_for_status()
        return response.json()

    async def create_pull_request_review(
        self,
        owner: str,
        repo: str,
        pull_number: int,
        body: str,
        comments: list | None = None,
    ):
        url = (
            f"{self.base_url}/repos/"
            f"{owner}/{repo}/pulls/{pull_number}/reviews"
        )

        payload = {
            "body": body,
            "event": "COMMENT",
        }

        if comments:
            payload["comments"] = comments

        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                headers=self.headers,
                json=payload,
            )

        response.raise_for_status()
        return response.json()