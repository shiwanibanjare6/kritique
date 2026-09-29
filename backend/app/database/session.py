from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from app.core.config import settings


database_url = settings.DATABASE_URL.strip()
if database_url.startswith("postgres://"):
    database_url = "postgresql+asyncpg://" + database_url.removeprefix("postgres://")
elif database_url.startswith("postgresql://"):
    database_url = "postgresql+asyncpg://" + database_url.removeprefix("postgresql://")
elif database_url.startswith("postgresql+psycopg://"):
    database_url = "postgresql+asyncpg://" + database_url.removeprefix("postgresql+psycopg://")

url = urlsplit(database_url)
query = dict(parse_qsl(url.query, keep_blank_values=True))
sslmode = query.pop("sslmode", None)
if sslmode:
    query["ssl"] = sslmode
database_url = urlunsplit(url._replace(query=urlencode(query)))

engine = create_async_engine(
    database_url,

    echo=settings.DEBUG,

    future=True

)


AsyncSessionLocal = async_sessionmaker(

    bind=engine,

    expire_on_commit=False,

    class_=AsyncSession

)


async def get_db():

    async with AsyncSessionLocal() as session:

        yield session
