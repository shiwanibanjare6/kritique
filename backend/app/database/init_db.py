from app.database.base import Base
from app.database.session import engine

# Import models so SQLAlchemy registers them
from app.models import *  # noqa: F401,F403


async def init_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)