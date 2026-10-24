from sqlalchemy import Boolean, Integer, String, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class PullRequestFile(Base):
    __tablename__ = "pull_request_files"

    id: Mapped[int] = mapped_column(primary_key=True)

    pull_request_id: Mapped[int] = mapped_column(
        ForeignKey("pull_requests.id", ondelete="CASCADE")
    )

    filename: Mapped[str] = mapped_column(String(500))

    status: Mapped[str] = mapped_column(String(50))

    additions: Mapped[int]

    deletions: Mapped[int]

    changes: Mapped[int]

    patch: Mapped[str | None]

    review_status: Mapped[str | None] = mapped_column(String(20), nullable=True)
    review_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    truncated: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="false")
