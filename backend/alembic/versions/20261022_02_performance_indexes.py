"""Add indexes for user-scoped lists and latest-review lookup.

Revision ID: 20261022_02
Revises: 20261022_01
Create Date: 2026-10-22
"""

from alembic import op

revision = "20261022_02"
down_revision = "20261022_01"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_pull_requests_repository_id "
        "ON pull_requests (repository_id)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_pull_requests_state "
        "ON pull_requests (state)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_reviews_pull_request_created_id "
        "ON reviews (pull_request_id, created_at, id)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_reviews_created_at "
        "ON reviews (created_at)"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_reviews_pull_request_created_id")
    op.execute("DROP INDEX IF EXISTS ix_reviews_created_at")
    op.execute("DROP INDEX IF EXISTS ix_pull_requests_state")
    op.execute("DROP INDEX IF EXISTS ix_pull_requests_repository_id")
