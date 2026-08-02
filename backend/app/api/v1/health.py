from fastapi import APIRouter

from app.schemas.response import APIResponse
from app.core.config import settings

router = APIRouter(
    prefix="/api/v1",
    tags=["Health"]
)


@router.get("/health", response_model=APIResponse)
async def health():

    return APIResponse(

        success=True,

        message="Service is healthy.",

        data={

            "application": settings.APP_NAME,

            "version": settings.APP_VERSION,

            "status": "Running"

        }

    )