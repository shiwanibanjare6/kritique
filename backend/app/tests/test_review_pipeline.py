import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock

from sqlalchemy.sql.elements import BinaryExpression
from sqlalchemy import UniqueConstraint

from app.models.pull_request import PullRequest
from app.models.repository import Repository
from app.models.review_job import ReviewJob
from app.models.webhook_event import WebhookEvent
from app.api.v1.pull_request import _review_status
from app.services.webhook_service import WebhookService


class MemorySession:
    def __init__(self, rows=None):
        self.rows = rows if rows is not None else {}
        self.pending = []
        self.next_id = 1

    async def scalar(self, statement):
        entity = statement.column_descriptions[0]["entity"]
        where = statement.whereclause
        expressions = list(where.clauses) if hasattr(where, "clauses") else [where]
        filters = {
            expression.left.key: expression.right.value
            for expression in expressions
            if isinstance(expression, BinaryExpression)
        }
        for row in [*self.rows.get(entity, []), *self.pending]:
            if isinstance(row, entity) and all(getattr(row, key) == value for key, value in filters.items()):
                return row
        return None

    def add(self, row):
        self.pending.append(row)

    async def flush(self):
        for row in self.pending:
            if getattr(row, "id", None) is None:
                row.id = self.next_id
                self.next_id += 1

    async def commit(self):
        await self.flush()
        for row in self.pending:
            self.rows.setdefault(type(row), []).append(row)
        self.pending.clear()

    async def refresh(self, _row):
        return None

    async def rollback(self):
        self.pending.clear()


def webhook_payload(sha="a" * 40):
    return {
        "action": "opened",
        "repository": {
            "id": 77,
            "owner": {"login": "octo"},
            "name": "sample",
            "full_name": "octo/sample",
            "default_branch": "main",
        },
        "pull_request": {
            "id": 9001,
            "number": 12,
            "html_url": "https://github.com/octo/sample/pull/12",
            "title": "Example PR",
            "user": {"login": "contributor"},
            "state": "open",
            "base": {"ref": "main"},
            "head": {"ref": "feature", "sha": sha},
        },
    }


def test_valid_webhook_persists_and_queues_job(monkeypatch):
    rows = {}
    queued = []
    monkeypatch.setattr(
        "app.services.webhook_service.enqueue_review_job",
        AsyncMock(side_effect=lambda _redis, job_id: queued.append(job_id) or True),
    )
    service = WebhookService(MemorySession(rows), redis=object())

    result = asyncio.run(service.process_pull_request(webhook_payload(), "pull_request", "delivery-1"))

    assert result["status"] == "queued"
    assert queued == [result["job_id"]]
    assert len(rows[ReviewJob]) == 1
    assert rows[ReviewJob][0].status == "queued"
    assert rows[WebhookEvent][0].delivery_id == "delivery-1"


def test_duplicate_delivery_and_same_revision_do_not_create_jobs(monkeypatch):
    rows = {}
    enqueue = AsyncMock(return_value=True)
    monkeypatch.setattr("app.services.webhook_service.enqueue_review_job", enqueue)
    service = WebhookService(MemorySession(rows), redis=object())

    first = asyncio.run(service.process_pull_request(webhook_payload(), "pull_request", "delivery-1"))
    repeated_delivery = asyncio.run(service.process_pull_request(webhook_payload(), "pull_request", "delivery-1"))
    repeated_revision = asyncio.run(service.process_pull_request(webhook_payload(), "pull_request", "delivery-2"))

    assert first["status"] == "queued"
    assert repeated_delivery["status"] == "duplicate"
    assert repeated_revision["status"] == "duplicate"
    assert len(rows[ReviewJob]) == 1
    enqueue.assert_awaited_once()


def test_new_revision_gets_a_new_job_and_failed_revision_stays_deduplicated(monkeypatch):
    rows = {}
    monkeypatch.setattr(
        "app.services.webhook_service.enqueue_review_job",
        AsyncMock(return_value=True),
    )
    service = WebhookService(MemorySession(rows), redis=object())

    first = asyncio.run(service.process_pull_request(webhook_payload(), "pull_request", "delivery-1"))
    second = asyncio.run(service.process_pull_request(webhook_payload("b" * 40), "pull_request", "delivery-2"))
    rows[ReviewJob][1].status = "failed"
    third = asyncio.run(service.process_pull_request(webhook_payload("b" * 40), "pull_request", "delivery-3"))

    assert second["status"] == "queued"
    assert third["status"] == "duplicate"
    assert len(rows[ReviewJob]) == 2
    assert rows[ReviewJob][0].id == first["job_id"]
    assert rows[ReviewJob][1].status == "failed"


def test_unsupported_event_is_ignored():
    result = asyncio.run(WebhookService(MemorySession()).process_pull_request(
        webhook_payload(), "issues", "delivery-1"
    ))
    assert result["status"] == "ignored"


def test_revision_and_delivery_uniqueness_are_database_constraints():
    revision_unique = next(
        constraint for constraint in ReviewJob.__table__.constraints
        if constraint.name == "uq_review_job_pr_revision"
    )
    delivery_unique = next(
        constraint for constraint in WebhookEvent.__table__.constraints
        if isinstance(constraint, UniqueConstraint)
        and any(column.name == "delivery_id" for column in constraint.columns)
    )
    assert {column.name for column in revision_unique.columns} == {"pull_request_id", "head_sha"}
    assert [column.name for column in delivery_unique.columns] == ["delivery_id"]


def test_review_status_tracks_current_revision_or_existing_review():
    pr = SimpleNamespace(head_sha="b" * 40)
    old_job = SimpleNamespace(head_sha="a" * 40, status="completed")
    current_job = SimpleNamespace(head_sha="b" * 40, status="processing")

    assert _review_status(pr, [old_job], None) == "pending"
    assert _review_status(pr, [current_job, old_job], None) == "processing"
    assert _review_status(pr, [], object()) == "completed"


class WorkerSession:
    def __init__(self, job):
        self.job = job
        self.added = []

    async def __aenter__(self):
        return self

    async def __aexit__(self, *_args):
        return False

    async def execute(self, _statement):
        return SimpleNamespace(
            scalar_one_or_none=lambda: self.job,
            scalar_one=lambda: self.job,
        )

    async def scalar(self, _statement):
        return self.job

    async def scalars(self, _statement):
        return []

    def add(self, row):
        self.added.append(row)

    def add_all(self, rows):
        self.added.extend(rows)

    async def delete(self, _row):
        return None

    async def commit(self):
        return None


def worker_job(job_id=1):
    repository = SimpleNamespace(id=77, owner="octo", name="sample", full_name="octo/sample")
    pull_request = SimpleNamespace(id=4, pr_number=12, repository=repository)
    return SimpleNamespace(
        id=job_id,
        status="queued",
        started_at=None,
        completed_at=None,
        error_message=None,
        attempt_count=0,
        pull_request=pull_request,
        repository_id=77,
        pull_request_id=4,
    )


def test_worker_success_persists_review_and_completes_job(monkeypatch):
    from app.services import review_job_service

    job = worker_job()
    sessions = []
    invalidate_cache = AsyncMock()
    monkeypatch.setattr(review_job_service.response_cache, "invalidate_all", invalidate_cache)

    def session_factory():
        session = WorkerSession(job)
        sessions.append(session)
        return session

    github = SimpleNamespace(
        get_pull_request_files=AsyncMock(return_value=[{
            "filename": "src/app.py", "patch": "@@ change", "status": "modified",
            "additions": 1, "deletions": 0, "changes": 1,
        }]),
        create_review=AsyncMock(),
    )
    ai = SimpleNamespace(
        review_code=AsyncMock(return_value={
            "summary": "Looks good", "security_score": 90, "style_score": 88,
            "architecture_score": 92, "final_score": 90, "comments": [],
            "status": "reviewed", "risk_level": "Low", "strengths": [],
            "weaknesses": [], "merge_recommendation": "Ready to Merge",
        }),
        review_pull_request=AsyncMock(return_value={
            "summary": "Review summary", "merge_recommendation": "Ready to Merge",
            "risk_level": "Low", "strengths": [], "weaknesses": [],
        }),
    )
    monkeypatch.setattr(review_job_service, "GitHubService", lambda: github)
    monkeypatch.setattr(review_job_service, "AIReviewService", lambda: ai)

    completed = asyncio.run(review_job_service.execute_review_job(1, session_factory))

    assert completed is True
    assert job.status == "completed"
    assert job.started_at is not None
    assert job.completed_at is not None
    assert job.attempt_count == 1
    assert any(type(item).__name__ == "Review" for session in sessions for item in session.added)
    invalidate_cache.assert_awaited_once()
    github.create_review.assert_awaited_once()


def test_worker_marks_failure_and_continues_to_next_job(monkeypatch):
    from app.services import review_job_service
    from app.workers import review_worker

    failed_job = worker_job(1)
    later_job = worker_job(2)
    sessions_by_call = []

    def session_factory():
        job = failed_job if len(sessions_by_call) < 3 else later_job
        session = WorkerSession(job)
        sessions_by_call.append(session)
        return session

    github = SimpleNamespace(
        get_pull_request_files=AsyncMock(side_effect=[RuntimeError("temporary provider error"), [{
            "filename": "src/app.py", "patch": "@@ change", "status": "modified",
            "additions": 1, "deletions": 0, "changes": 1,
        }]]),
        create_review=AsyncMock(),
    )
    ai = SimpleNamespace(
        review_code=AsyncMock(return_value={
            "status": "reviewed", "summary": "Looks good", "security_score": 90,
            "style_score": 90, "architecture_score": 90, "final_score": 90,
            "risk_level": "Low", "strengths": [], "weaknesses": [],
            "merge_recommendation": "Ready to Merge", "comments": [],
        }),
        review_pull_request=AsyncMock(return_value={
            "summary": "Review summary", "merge_recommendation": "Ready to Merge",
            "risk_level": "Low", "strengths": [], "weaknesses": [],
        }),
    )
    monkeypatch.setattr(review_job_service, "GitHubService", lambda: github)
    monkeypatch.setattr(review_job_service, "AIReviewService", lambda: ai)
    monkeypatch.setattr(
        review_worker,
        "execute_review_job",
        lambda job_id: review_job_service.execute_review_job(job_id, session_factory),
    )

    async def process_both_jobs():
        await review_worker.process_review_job_message(1)
        await review_worker.process_review_job_message(2)

    asyncio.run(process_both_jobs())

    assert failed_job.status == "failed"
    assert "temporary provider error" in failed_job.error_message
    assert later_job.status == "completed"


def test_worker_excludes_failed_files_and_persists_counts_for_successful_files(monkeypatch):
    from app.models.pull_request_file import PullRequestFile
    from app.models.review import Review
    from app.services import review_job_service

    job = worker_job()
    sessions = []

    def session_factory():
        session = WorkerSession(job)
        sessions.append(session)
        return session

    github = SimpleNamespace(
        get_pull_request_files=AsyncMock(return_value=[
            {"filename": "src/ok.py", "patch": "@@ ok", "status": "modified", "additions": 1, "deletions": 0, "changes": 1},
            {"filename": "src/fail.py", "patch": "@@ fail", "status": "modified", "additions": 1, "deletions": 0, "changes": 1},
        ]),
        create_review=AsyncMock(),
    )
    good = {
        "status": "reviewed", "summary": "Good change", "security_score": 90,
        "style_score": 80, "architecture_score": 70, "final_score": 80,
        "risk_level": "Low", "strengths": [], "weaknesses": [],
        "merge_recommendation": "Ready to Merge", "comments": [],
    }
    ai = SimpleNamespace(
        review_code=AsyncMock(side_effect=[good, RuntimeError("invalid response")]),
        review_pull_request=AsyncMock(return_value={
            "summary": "One file was reviewed.", "summary_source": "model",
        }),
        pipeline_metrics=[],
    )
    monkeypatch.setattr(review_job_service, "GitHubService", lambda: github)
    monkeypatch.setattr(review_job_service, "AIReviewService", lambda: ai)

    completed = asyncio.run(review_job_service.execute_review_job(1, session_factory))

    assert completed is True
    review = next(item for session in sessions for item in session.added if isinstance(item, Review))
    file_rows = [item for session in sessions for item in session.added if isinstance(item, PullRequestFile)]
    assert review.files_reviewed == 1
    assert review.files_failed == 1
    assert review.final_score == 80
    assert [row.review_status for row in file_rows] == ["reviewed", "failed"]
    assert [entry["review"]["status"] for entry in review.agent_output] == ["reviewed", "failed"]


def test_worker_fails_job_when_every_file_review_fails_without_storing_review(monkeypatch):
    from app.models.pull_request_file import PullRequestFile
    from app.models.review import Review
    from app.services import review_job_service

    job = worker_job()
    sessions = []

    def session_factory():
        session = WorkerSession(job)
        sessions.append(session)
        return session

    github = SimpleNamespace(
        get_pull_request_files=AsyncMock(return_value=[
            {"filename": "src/fail.py", "patch": "@@ fail", "status": "modified", "additions": 1, "deletions": 0, "changes": 1},
        ]),
        create_review=AsyncMock(),
    )
    ai = SimpleNamespace(
        review_code=AsyncMock(side_effect=RuntimeError("validation failed")),
        pipeline_metrics=[],
    )
    monkeypatch.setattr(review_job_service, "GitHubService", lambda: github)
    monkeypatch.setattr(review_job_service, "AIReviewService", lambda: ai)

    completed = asyncio.run(review_job_service.execute_review_job(1, session_factory))

    assert completed is False
    assert job.status == "failed"
    assert "files_failed=1" in job.error_message
    assert not any(isinstance(item, Review) for session in sessions for item in session.added)
    file_rows = [item for session in sessions for item in session.added if isinstance(item, PullRequestFile)]
    assert file_rows[0].review_status == "failed"
