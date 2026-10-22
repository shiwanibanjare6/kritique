import httpx
from time import perf_counter
from fastapi import Header, HTTPException

from app.core.config import settings
from app.middleware.sql_metrics import sql_request_metrics
from app.services.github_service import GitHubService


async def get_github_login(authorization: str = Header(...)) -> str:
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token.strip():
        raise HTTPException(status_code=401, detail="GitHub access token required")

    started = perf_counter()
    try:
        user = await GitHubService(token.strip()).get_authenticated_user()
    except httpx.HTTPStatusError as error:
        if error.response.status_code in (401, 403):
            raise HTTPException(status_code=401, detail="Invalid or expired GitHub access token") from error
        raise HTTPException(status_code=502, detail="GitHub authentication lookup failed") from error
    except httpx.HTTPError as error:
        raise HTTPException(status_code=502, detail="GitHub authentication lookup failed") from error
    finally:
        if settings.DEBUG_SQL:
            metrics = sql_request_metrics.get()
            if metrics is not None:
                metrics.auth_time_ms = (perf_counter() - started) * 1000

    return user["login"]
