"""Persist multi-agent review metrics and per-file outcomes.

Revision ID: 20261022_03
Revises: 20261022_02
Create Date: 2026-10-22
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy import inspect

revision = "20261022_03"
down_revision = "20261022_02"
branch_labels = None
depends_on = None


def _add_if_missing(table: str, column: sa.Column) -> None:
    existing = {item["name"] for item in inspect(op.get_bind()).get_columns(table)}
    if column.name not in existing:
        op.add_column(table, column)


def upgrade() -> None:
    tables = set(inspect(op.get_bind()).get_table_names())
    if "reviews" in tables:
        _add_if_missing("reviews", sa.Column("pipeline_metrics", sa.JSON(), nullable=True))
        _add_if_missing("reviews", sa.Column("duration_ms", sa.Integer(), nullable=True))
        _add_if_missing("reviews", sa.Column("files_reviewed", sa.Integer(), nullable=True))
        _add_if_missing("reviews", sa.Column("files_skipped", sa.Integer(), nullable=True))
        _add_if_missing("reviews", sa.Column("files_failed", sa.Integer(), nullable=True))
        _add_if_missing("reviews", sa.Column("summary_source", sa.String(length=30), nullable=True))
    if "pull_request_files" in tables:
        _add_if_missing("pull_request_files", sa.Column("review_status", sa.String(length=20), nullable=True))
        _add_if_missing("pull_request_files", sa.Column("review_error", sa.Text(), nullable=True))
        _add_if_missing(
            "pull_request_files",
            sa.Column("truncated", sa.Boolean(), nullable=False, server_default=sa.false()),
        )


def downgrade() -> None:
    tables = set(inspect(op.get_bind()).get_table_names())
    for table, names in (
        ("pull_request_files", ("truncated", "review_error", "review_status")),
        ("reviews", ("summary_source", "files_failed", "files_skipped", "files_reviewed", "duration_ms", "pipeline_metrics")),
    ):
        if table not in tables:
            continue
        existing = {item["name"] for item in inspect(op.get_bind()).get_columns(table)}
        for name in names:
            if name in existing:
                op.drop_column(table, name)
