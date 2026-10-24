from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class AgentFinding(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    line: int | None
    severity: Literal["info", "warning", "critical"]
    category: str = Field(min_length=1)
    message: str = Field(min_length=1)
    suggestion: str | None


class AgentResult(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    agent: Literal["security", "style", "architecture"]
    score: int = Field(ge=0, le=100)
    summary: str = Field(min_length=1)
    reason: str = Field(min_length=1)
    findings: list[AgentFinding]


class OverallSummaryResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    summary: str = Field(min_length=1)


class LegacyReviewComment(BaseModel):
    model_config = ConfigDict(extra="forbid")

    line: int | None
    severity: Literal["info", "warning", "critical"]
    comment: str = Field(min_length=1)


class LegacyFileReview(BaseModel):
    model_config = ConfigDict(extra="forbid")

    summary: str = Field(min_length=1)
    security_score: int = Field(ge=0, le=100)
    security_reason: str
    style_score: int = Field(ge=0, le=100)
    style_reason: str
    architecture_score: int = Field(ge=0, le=100)
    architecture_reason: str
    final_score: int = Field(ge=0, le=100)
    risk_level: Literal["Low", "Medium", "High"]
    strengths: list[str]
    weaknesses: list[str]
    merge_recommendation: Literal[
        "Ready to Merge", "Merge After Minor Changes", "Changes Required"
    ]
    comments: list[LegacyReviewComment]


class LegacyPullRequestReview(BaseModel):
    model_config = ConfigDict(extra="forbid")

    summary: str = Field(min_length=1)
    merge_recommendation: Literal[
        "Ready to Merge", "Merge After Minor Changes", "Changes Required"
    ]
    risk_level: Literal["Low", "Medium", "High"]
    strengths: list[str]
    weaknesses: list[str]
