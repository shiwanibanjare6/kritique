import asyncio
from datetime import date, datetime, time, timedelta

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.api.v1.pull_request import get_pull_requests
from app.database.base import Base
from app.models.pull_request import PullRequest
from app.models.repository import Repository
from app.models.repository_connection import RepositoryConnection
from app.models.review import Review
from app.services.performance_queries import (
    get_pull_request_summary,
    get_review_timeseries,
    get_stats_summary,
    list_pull_request_rows,
)
from app.services.response_cache import TTLResponseCache


class AsyncSessionAdapter:
    """Lets async query functions run against SQLite without aiosqlite."""

    def __init__(self, session: Session):
        self.session = session

    async def execute(self, statement):
        return self.session.execute(statement)

    async def scalar(self, statement):
        return self.session.scalar(statement)

    async def scalars(self, statement):
        return self.session.scalars(statement)


def database():
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    session = Session(engine)
    repository = Repository(
        github_id=101,
        owner="octo",
        name="sample",
        full_name="octo/sample",
        default_branch="main",
    )
    session.add(repository)
    session.flush()
    session.add(RepositoryConnection(repository_id=repository.id, github_login="alice"))
    pull_requests = [
        PullRequest(
            repository_id=repository.id,
            github_pr_id=1001,
            html_url="https://github.com/octo/sample/pull/1",
            pr_number=1,
            title="Feature alpha",
            author="dev-one",
            state="open",
            base_branch="main",
            head_branch="feature-alpha",
            head_sha="a" * 40,
            updated_at=datetime(2026, 10, 20),
        ),
        PullRequest(
            repository_id=repository.id,
            github_pr_id=1002,
            html_url="https://github.com/octo/sample/pull/2",
            pr_number=2,
            title="Bug fix beta",
            author="dev-two",
            state="closed",
            base_branch="main",
            head_branch="bug-fix",
            head_sha="b" * 40,
            updated_at=datetime(2026, 10, 21),
        ),
    ]
    session.add_all(pull_requests)
    session.flush()
    today = date.today()
    session.add_all([
        Review(
            pull_request_id=pull_requests[0].id,
            summary="older review",
            final_score=20,
            security_score=25,
            style_score=30,
            architecture_score=35,
            created_at=datetime.combine(today - timedelta(days=2), time(12)),
            agent_output={"source": "older"},
        ),
        Review(
            pull_request_id=pull_requests[0].id,
            summary="latest review",
            final_score=90,
            security_score=91,
            style_score=92,
            architecture_score=93,
            created_at=datetime.combine(today - timedelta(days=1), time(12)),
            agent_output={"source": "latest"},
        ),
        Review(
            pull_request_id=pull_requests[1].id,
            summary="second PR review",
            final_score=70,
            security_score=71,
            style_score=72,
            architecture_score=73,
            created_at=datetime.combine(today - timedelta(days=1), time(14)),
            agent_output={"source": "second"},
        ),
    ])
    session.commit()
    return engine, session, AsyncSessionAdapter(session), pull_requests


def test_latest_review_is_selected_in_sql_for_multiple_reviews():
    engine, session, db, pull_requests = database()
    try:
        rows = asyncio.run(list_pull_request_rows(db, "alice", include_agent_output=True))
        latest = {pr.id: review for pr, review in rows}
        assert latest[pull_requests[0].id].summary == "latest review"
        assert latest[pull_requests[0].id].agent_output == {"source": "latest"}
    finally:
        session.close()
        engine.dispose()


def test_stats_aggregate_latest_review_per_pull_request():
    engine, session, db, _pull_requests = database()
    try:
        stats = asyncio.run(get_stats_summary(db, "alice"))
        assert stats["total_repositories"] == 1
        assert stats["total_pull_requests"] == 2
        assert stats["reviewed_pull_requests"] == 2
        assert stats["average_final_score"] == 80
        assert stats["average_security_score"] == 81
        assert stats["average_style_score"] == 82
        assert stats["average_architecture_score"] == 83
        assert stats["highest_final_score"] == 90
        assert stats["lowest_final_score"] == 70
    finally:
        session.close()
        engine.dispose()


def test_timeseries_fills_days_without_reviews_with_zeros():
    engine, session, db, _pull_requests = database()
    try:
        series = asyncio.run(get_review_timeseries(db, "alice", days=4))
        assert len(series) == 4
        assert series[0]["review_count"] == 0
        assert series[0]["average_score"] == 0
        assert series[1]["review_count"] == 1
        assert series[1]["average_score"] == 20
        assert series[2]["review_count"] == 2
        assert series[2]["average_score"] == 80
        assert series[3]["review_count"] == 0
        assert series[3]["average_score"] == 0
    finally:
        session.close()
        engine.dispose()


def test_pull_request_summary_filters_and_paginates_without_agent_output():
    from sqlalchemy import event

    engine, session, db, _pull_requests = database()
    try:
        statements = []
        event.listen(
            session.bind,
            "before_cursor_execute",
            lambda _connection, _cursor, statement, _parameters, _context, _executemany: statements.append(statement.lower()),
        )
        page = asyncio.run(get_pull_request_summary(
            db,
            "alice",
            limit=1,
            offset=0,
            state="OPEN",
            q="alpha",
        ))
        assert page["total"] == 1
        assert len(page["items"]) == 1
        assert page["items"][0]["pr_number"] == 1
        assert page["items"][0]["latest_review"]["final_score"] == 90
        assert "agent_output" not in page["items"][0]["latest_review"]
        assert all("agent_output" not in statement for statement in statements)
        next_page = asyncio.run(get_pull_request_summary(
            db,
            "alice",
            limit=1,
            offset=1,
            state=None,
            q=None,
        ))
        assert next_page["total"] == 2
        assert next_page["items"][0]["pr_number"] == 1
    finally:
        session.close()
        engine.dispose()


def test_existing_pull_request_endpoint_keeps_its_response_shape():
    from sqlalchemy import event

    engine, session, db, _pull_requests = database()
    try:
        statements = []
        event.listen(
            session.bind,
            "before_cursor_execute",
            lambda _connection, _cursor, statement, _parameters, _context, _executemany: statements.append(statement.lower()),
        )
        response = asyncio.run(get_pull_requests(db, "alice"))
        item = next(value for value in response if value["pr_number"] == 1)
        assert set(item) == {
            "id", "pr_number", "title", "author", "state", "base_branch",
            "head_branch", "repository", "latest_review", "review_status",
        }
        assert item["latest_review"]["summary"] == "latest review"
        assert item["latest_review"]["agent_output"] == {"source": "latest"}
        assert len(statements) == 2
    finally:
        session.close()
        engine.dispose()


def test_response_cache_hit_miss_user_isolation_and_invalidation():
    async def run():
        cache = TTLResponseCache(ttl_seconds=30)
        calls = 0

        async def load():
            nonlocal calls
            calls += 1
            return {"calls": calls}

        first, first_status = await cache.get_or_set("alice", "stats", load)
        same, same_status = await cache.get_or_set("alice", "stats", load)
        other, other_status = await cache.get_or_set("bob", "stats", load)
        assert (first_status, same_status, other_status) == ("MISS", "HIT", "MISS")
        assert first == same and first != other
        await cache.invalidate_user("alice")
        refreshed, refreshed_status = await cache.get_or_set("alice", "stats", load)
        assert refreshed_status == "MISS"
        assert refreshed["calls"] == 3

    asyncio.run(run())
