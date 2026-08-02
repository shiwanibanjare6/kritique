from sqlalchemy import Integer, String, ForeignKey
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