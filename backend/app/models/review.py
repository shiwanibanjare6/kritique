from datetime import datetime

from sqlalchemy import DateTime
from sqlalchemy import Float
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import JSON
from sqlalchemy import Text
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from app.database.base import Base


class Review(Base):
    __tablename__ = "reviews"

    id: Mapped[int] = mapped_column(primary_key=True)

    pull_request_id: Mapped[int] = mapped_column(
        ForeignKey("pull_requests.id"),
        nullable=False,
    )

    summary: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    security_score: Mapped[float] = mapped_column(
        Float,
        default=0.0,
    )

    style_score: Mapped[float] = mapped_column(
        Float,
        default=0.0,
    )

    architecture_score: Mapped[float] = mapped_column(
        Float,
        default=0.0,
    )

    final_score: Mapped[float] = mapped_column(
        Float,
        default=0.0,
    )

    agent_output: Mapped[dict] = mapped_column(
        JSON,
        default=dict,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )

    pull_request = relationship(
        "PullRequest",
        back_populates="reviews",
    )