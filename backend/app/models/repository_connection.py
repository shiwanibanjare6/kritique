from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class RepositoryConnection(Base):
    __tablename__ = "repository_connections"

    repository_id: Mapped[int] = mapped_column(
        ForeignKey("repositories.id", ondelete="CASCADE"), primary_key=True
    )
    github_login: Mapped[str] = mapped_column(String(100), primary_key=True)

    repository = relationship("Repository", back_populates="connected_users")
