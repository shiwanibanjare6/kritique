from datetime import datetime

from sqlalchemy import BigInteger, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Repository(Base):
    __tablename__ = "repositories"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    github_id: Mapped[int] = mapped_column(
        BigInteger,
        unique=True,
        nullable=False,
    )

    owner: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    full_name: Mapped[str] = mapped_column(
        String(300),
        unique=True,
        nullable=False,
    )

    default_branch: Mapped[str] = mapped_column(
        String(100),
        default="main",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    pull_requests = relationship(
        "PullRequest",
        back_populates="repository",
        cascade="all, delete-orphan",
    )

    webhook_events = relationship(
        "WebhookEvent",
        back_populates="repository",
        cascade="all, delete-orphan",
    )