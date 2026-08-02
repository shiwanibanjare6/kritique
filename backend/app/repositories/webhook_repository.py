from sqlalchemy import select
from app.models.webhook_event import WebhookEvent
from sqlalchemy.ext.asyncio import AsyncSession

class WebhookRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_delivery_id(self, delivery_id: str):
        result = await self.db.execute(
            select(WebhookEvent).where(
                WebhookEvent.delivery_id == delivery_id
            )
        )
        return result.scalar_one_or_none()

    async def create(self, **kwargs):
        event = WebhookEvent(**kwargs)
        self.db.add(event)
        await self.db.commit()
        await self.db.refresh(event)
        return event