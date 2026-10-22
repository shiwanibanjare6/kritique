from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy import event
from time import perf_counter
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from app.core.config import settings
from app.middleware.sql_metrics import sql_request_metrics


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


if settings.DEBUG_SQL:
    @event.listens_for(engine.sync_engine, "before_cursor_execute")
    def _start_sql_timer(_connection, _cursor, _statement, _parameters, context, _executemany):
        context._kritique_sql_started = perf_counter()

    @event.listens_for(engine.sync_engine, "after_cursor_execute")
    def _record_sql_timer(_connection, _cursor, _statement, _parameters, context, _executemany):
        metrics = sql_request_metrics.get()
        started = getattr(context, "_kritique_sql_started", None)
        if metrics is not None and started is not None:
            metrics.query_count += 1
            metrics.db_time_ms += (perf_counter() - started) * 1000


AsyncSessionLocal = async_sessionmaker(

    bind=engine,

    expire_on_commit=False,

    class_=AsyncSession

)


async def get_db():

    async with AsyncSessionLocal() as session:

        yield session
