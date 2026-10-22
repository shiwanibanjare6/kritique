"""Create missing application tables without altering existing tables.

Revision ID: 20261022_01
Revises:
Create Date: 2026-10-22
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy import inspect

from app import models  # noqa: F401
from app.database.base import Base

revision = "20261022_01"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    Base.metadata.create_all(bind=bind, checkfirst=True)
    inspector = inspect(bind)
    if "pull_requests" in inspector.get_table_names():
        columns = {column["name"] for column in inspector.get_columns("pull_requests")}
        if "head_sha" not in columns:
            op.add_column("pull_requests", sa.Column("head_sha", sa.String(40), nullable=True))


def downgrade() -> None:
    # This bootstrap is deliberately non-destructive on databases that predate Alembic.
    pass
