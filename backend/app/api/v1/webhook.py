from fastapi import APIRouter
from fastapi import Depends
from fastapi import Header
from fastapi import HTTPException
from fastapi import Request

from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.services.webhook_service import WebhookService
from app.utils.hmac_verify import verify_signature
from app.core.config import settings

router = APIRouter(
    prefix="/api/v1",
    tags=["Webhook"],
)


@router.post("/webhook")
async def github_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db),
    x_github_event: str = Header(...),
    x_github_delivery: str = Header(...),
    x_hub_signature_256: str = Header(...),
):

    body = await request.body()

    if not verify_signature(
    body,
    x_hub_signature_256.replace("sha256=", ""),
    settings.GITHUB_SECRET,
    ):
      raise HTTPException(
        status_code=401,
        detail="Invalid Signature",
    )

    payload = await request.json()
    
    if x_github_event == "ping":
        return {
            "status": "ok",
            "message": "Webhook verified successfully"
        }

    service = WebhookService(db)

    result = await service.process_pull_request(
        payload,
        x_github_event,
        x_github_delivery,
    )

    return result