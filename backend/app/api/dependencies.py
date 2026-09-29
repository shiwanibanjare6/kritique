import httpx
from fastapi import Header, HTTPException

from app.services.github_service import GitHubService


async def get_github_login(authorization: str = Header(...)) -> str:
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token.strip():
        raise HTTPException(status_code=401, detail="GitHub access token required")

    try:
        user = await GitHubService(token.strip()).get_authenticated_user()
    except httpx.HTTPStatusError as error:
        if error.response.status_code in (401, 403):
            raise HTTPException(status_code=401, detail="Invalid or expired GitHub access token") from error
        raise HTTPException(status_code=502, detail="GitHub authentication lookup failed") from error
    except httpx.HTTPError as error:
        raise HTTPException(status_code=502, detail="GitHub authentication lookup failed") from error

    return user["login"]
