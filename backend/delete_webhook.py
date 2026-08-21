import asyncio
import selectors

from sqlalchemy import delete

from app.database.session import engine
from app.models.webhook_event import WebhookEvent


DELIVERY_ID = "6f4d6d50-9ccd-11f1-8919-f77a5f1c7658"


async def main():
    async with engine.begin() as conn:
        result = await conn.execute(
            delete(WebhookEvent).where(
                WebhookEvent.delivery_id == DELIVERY_ID
            )
        )

        print(f"Deleted webhook events: {result.rowcount}")


if __name__ == "__main__":
    asyncio.run(
        main(),
        loop_factory=asyncio.SelectorEventLoop,
    )