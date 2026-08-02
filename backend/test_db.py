import asyncio
from sqlalchemy.ext.asyncio import create_async_engine

DATABASE_URL = "postgresql+asyncpg://postgres:shiwani@localhost:5432/ai_pr_reviewer"

engine = create_async_engine(DATABASE_URL)


async def test():
    async with engine.connect() as conn:
        print("✅ Database Connected Successfully!")


asyncio.run(test())