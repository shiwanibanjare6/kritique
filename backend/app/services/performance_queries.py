from datetime import date, timedelta

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased, joinedload, load_only

from app.models.pull_request import PullRequest
from app.models.repository import Repository
from app.models.repository_connection import RepositoryConnection
from app.models.review import Review
from app.models.review_job import ReviewJob


def latest_reviews_ranked(*, include_review_details: bool = False, include_agent_output: bool = False):
    """One SQL row-number window for selecting the newest review per PR."""
    columns = [
        Review.id,
        Review.pull_request_id,
        Review.created_at,
        Review.security_score,
        Review.style_score,
        Review.architecture_score,
        Review.final_score,
        Review.merge_recommendation,
        Review.risk_level,
    ]
    if include_review_details:
        columns.extend([Review.summary, Review.strengths, Review.weaknesses])
    if include_agent_output:
        columns.append(Review.agent_output)
    return (
        select(
            *columns,
            func.row_number()
            .over(
                partition_by=Review.pull_request_id,
                order_by=(Review.created_at.desc(), Review.id.desc()),
            )
            .label("review_rank"),
        )
    )


async def list_pull_request_rows(
    db: AsyncSession,
    github_login: str,
    *,
    include_agent_output: bool,
):
    ranked = latest_reviews_ranked(
        include_review_details=True,
        include_agent_output=include_agent_output,
    ).subquery("ranked_reviews")
    latest_review = aliased(Review, ranked)
    review_columns = [
        latest_review.id,
        latest_review.pull_request_id,
        latest_review.summary,
        latest_review.security_score,
        latest_review.style_score,
        latest_review.architecture_score,
        latest_review.final_score,
        latest_review.merge_recommendation,
        latest_review.risk_level,
        latest_review.strengths,
        latest_review.weaknesses,
        latest_review.created_at,
    ]
    if include_agent_output:
        review_columns.append(latest_review.agent_output)

    result = await db.execute(
        select(PullRequest, latest_review)
        .join(RepositoryConnection, RepositoryConnection.repository_id == PullRequest.repository_id)
        .options(
            joinedload(PullRequest.repository),
            load_only(PullRequest.id, PullRequest.pr_number, PullRequest.title, PullRequest.author,
                      PullRequest.state, PullRequest.base_branch, PullRequest.head_branch,
                      PullRequest.head_sha, PullRequest.repository_id, PullRequest.updated_at),
            load_only(*review_columns),
        )
        .outerjoin(
            latest_review,
            (latest_review.pull_request_id == PullRequest.id) & (ranked.c.review_rank == 1),
        )
        .where(RepositoryConnection.github_login == github_login)
        .order_by(PullRequest.updated_at.desc(), PullRequest.id.desc())
    )
    return result.unique().all()


async def list_review_jobs(db: AsyncSession, pull_request_ids: list[int]):
    if not pull_request_ids:
        return []
    ranked_jobs = (
        select(
            ReviewJob.pull_request_id,
            ReviewJob.head_sha,
            ReviewJob.status,
            func.row_number()
            .over(
                partition_by=ReviewJob.pull_request_id,
                order_by=(ReviewJob.created_at.desc(), ReviewJob.id.desc()),
            )
            .label("job_rank"),
        )
        .join(PullRequest, PullRequest.id == ReviewJob.pull_request_id)
        .where(
            ReviewJob.pull_request_id.in_(pull_request_ids),
            or_(PullRequest.head_sha.is_(None), ReviewJob.head_sha == PullRequest.head_sha),
        )
        .subquery("ranked_review_jobs")
    )
    result = await db.execute(
        select(
            ranked_jobs.c.pull_request_id,
            ranked_jobs.c.head_sha,
            ranked_jobs.c.status,
        ).where(ranked_jobs.c.job_rank == 1)
    )
    return result.all()


def review_status_by_pull_request(pull_requests, jobs, latest_reviews):
    jobs_by_pr: dict[int, list[ReviewJob]] = {}
    for job in jobs:
        jobs_by_pr.setdefault(job.pull_request_id, []).append(job)
    statuses = {}
    for pr in pull_requests:
        latest_review = latest_reviews.get(pr.id)
        status = "completed" if latest_review is not None else "pending"
        for job in jobs_by_pr.get(pr.id, []):
            if pr.head_sha is None or job.head_sha == pr.head_sha:
                status = job.status
                break
        statuses[pr.id] = status
    return statuses


def user_pull_requests(github_login: str):
    return (
        select(PullRequest.id, PullRequest.repository_id)
        .join(RepositoryConnection, RepositoryConnection.repository_id == PullRequest.repository_id)
        .where(RepositoryConnection.github_login == github_login)
    )


async def get_stats_summary(db: AsyncSession, github_login: str) -> dict:
    scoped_prs = user_pull_requests(github_login).cte("user_pull_requests")
    ranked_reviews = latest_reviews_ranked().cte("ranked_reviews_for_user")
    latest_scores = (
        select(
            ranked_reviews.c.pull_request_id,
            ranked_reviews.c.final_score,
            ranked_reviews.c.security_score,
            ranked_reviews.c.style_score,
            ranked_reviews.c.architecture_score,
        )
        .join(scoped_prs, scoped_prs.c.id == ranked_reviews.c.pull_request_id)
        .where(ranked_reviews.c.review_rank == 1)
        .cte("latest_user_review_scores")
    )
    repositories_count = (
        select(func.count(func.distinct(RepositoryConnection.repository_id)))
        .where(RepositoryConnection.github_login == github_login)
        .scalar_subquery()
    )
    pull_requests_count = select(func.count()).select_from(scoped_prs).scalar_subquery()
    aggregates = select(
        func.count().label("reviewed_pull_requests"),
        func.avg(latest_scores.c.final_score).label("average_final_score"),
        func.avg(latest_scores.c.security_score).label("average_security_score"),
        func.avg(latest_scores.c.style_score).label("average_style_score"),
        func.avg(latest_scores.c.architecture_score).label("average_architecture_score"),
        func.max(latest_scores.c.final_score).label("highest_final_score"),
        func.min(latest_scores.c.final_score).label("lowest_final_score"),
    ).select_from(latest_scores).cte("review_aggregates")
    row = (
        await db.execute(
            select(
                repositories_count.label("total_repositories"),
                pull_requests_count.label("total_pull_requests"),
                aggregates.c.reviewed_pull_requests,
                aggregates.c.average_final_score,
                aggregates.c.average_security_score,
                aggregates.c.average_style_score,
                aggregates.c.average_architecture_score,
                aggregates.c.highest_final_score,
                aggregates.c.lowest_final_score,
            )
        )
    ).mappings().one()
    return dict(row)


async def get_review_timeseries(db: AsyncSession, github_login: str, days: int) -> list[dict]:
    today = date.today()
    start_date = today - timedelta(days=days - 1)
    result = await db.execute(
        select(
            func.date(Review.created_at).label("review_date"),
            func.count(Review.id).label("review_count"),
            func.avg(Review.final_score).label("average_score"),
        )
        .join(PullRequest, PullRequest.id == Review.pull_request_id)
        .join(RepositoryConnection, RepositoryConnection.repository_id == PullRequest.repository_id)
        .where(
            RepositoryConnection.github_login == github_login,
            Review.created_at >= start_date,
            Review.created_at < today + timedelta(days=1),
        )
        .group_by(func.date(Review.created_at))
        .order_by(func.date(Review.created_at))
    )
    by_date = {}
    for row in result.mappings():
        key = row["review_date"].isoformat() if hasattr(row["review_date"], "isoformat") else str(row["review_date"])
        by_date[key] = {
            "review_count": int(row["review_count"]),
            "average_score": float(row["average_score"] or 0),
        }
    return [
        {
            "date": (start_date + timedelta(days=index)).isoformat(),
            **by_date.get((start_date + timedelta(days=index)).isoformat(), {
                "review_count": 0,
                "average_score": 0.0,
            }),
        }
        for index in range(days)
    ]


async def get_pull_request_summary(
    db: AsyncSession,
    github_login: str,
    *,
    limit: int,
    offset: int,
    state: str | None,
    q: str | None,
) -> dict:
    base = (
        select(PullRequest.id)
        .join(RepositoryConnection, RepositoryConnection.repository_id == PullRequest.repository_id)
        .join(Repository, Repository.id == PullRequest.repository_id)
        .where(RepositoryConnection.github_login == github_login)
    )
    if state:
        base = base.where(func.lower(PullRequest.state) == state.casefold())
    if q:
        pattern = f"%{q.strip()}%"
        base = base.where(
            PullRequest.title.ilike(pattern)
            | PullRequest.author.ilike(pattern)
            | Repository.name.ilike(pattern)
            | Repository.full_name.ilike(pattern)
        )
    count = await db.scalar(select(func.count()).select_from(base.subquery()))
    ranked = latest_reviews_ranked().subquery("ranked_reviews")
    latest_review = aliased(Review, ranked)
    rows = (
        await db.execute(
            select(PullRequest, latest_review)
            .join(RepositoryConnection, RepositoryConnection.repository_id == PullRequest.repository_id)
            .options(
                joinedload(PullRequest.repository),
                load_only(PullRequest.id, PullRequest.pr_number, PullRequest.title, PullRequest.author,
                          PullRequest.state, PullRequest.base_branch, PullRequest.head_branch,
                          PullRequest.repository_id, PullRequest.updated_at),
                load_only(
                    latest_review.id,
                    latest_review.pull_request_id,
                    latest_review.final_score,
                    latest_review.security_score,
                    latest_review.style_score,
                    latest_review.architecture_score,
                    latest_review.merge_recommendation,
                    latest_review.risk_level,
                    latest_review.created_at,
                ),
            )
            .outerjoin(
                latest_review,
                (latest_review.pull_request_id == PullRequest.id) & (ranked.c.review_rank == 1),
            )
            .where(PullRequest.id.in_(base))
            .order_by(PullRequest.updated_at.desc(), PullRequest.id.desc())
            .limit(limit)
            .offset(offset)
        )
    ).unique().all()
    jobs = await list_review_jobs(db, [pr.id for pr, _review in rows])
    statuses = review_status_by_pull_request(
        [pr for pr, _review in rows],
        jobs,
        {pr.id: review for pr, review in rows if review is not None},
    )
    items = []
    for pr, review in rows:
        items.append({
            "id": pr.id,
            "pr_number": pr.pr_number,
            "title": pr.title,
            "author": pr.author,
            "state": pr.state,
            "base_branch": pr.base_branch,
            "head_branch": pr.head_branch,
            "review_status": statuses[pr.id],
            "repository": {
                "id": pr.repository.id,
                "name": pr.repository.name,
                "full_name": pr.repository.full_name,
                "owner": pr.repository.owner,
            },
            "latest_review": None if review is None else {
                "final_score": review.final_score,
                "security_score": review.security_score,
                "style_score": review.style_score,
                "architecture_score": review.architecture_score,
                "merge_recommendation": review.merge_recommendation,
                "risk_level": review.risk_level,
                "created_at": review.created_at,
            },
        })
    return {"items": items, "total": int(count or 0)}
