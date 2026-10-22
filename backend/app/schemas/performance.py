from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class RepositorySummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    full_name: str
    owner: str


class LatestReviewSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    final_score: float
    security_score: float
    style_score: float
    architecture_score: float
    merge_recommendation: str
    risk_level: str
    created_at: datetime


class PullRequestSummaryItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    pr_number: int
    title: str
    author: str
    state: str
    base_branch: str
    head_branch: str
    review_status: str
    repository: RepositorySummary
    latest_review: LatestReviewSummary | None


class PullRequestSummaryResponse(BaseModel):
    items: list[PullRequestSummaryItem]
    total: int


class StatsSummary(BaseModel):
    total_repositories: int
    total_pull_requests: int
    reviewed_pull_requests: int
    average_final_score: float | None
    average_security_score: float | None
    average_style_score: float | None
    average_architecture_score: float | None
    highest_final_score: float | None
    lowest_final_score: float | None


class TimeseriesPoint(BaseModel):
    date: str
    review_count: int = Field(ge=0)
    average_score: float = Field(ge=0)


class TimeseriesResponse(BaseModel):
    items: list[TimeseriesPoint]
