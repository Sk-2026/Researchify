
import uuid

from sqlalchemy import String, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, UUIDMixin, TimestampMixin


class ResearchProfile(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "research_profiles"

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )

    domain: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    timezone: Mapped[str] = mapped_column(
        String(100),
        default="Asia/Kolkata",
        nullable=False,
    )

    digest_time: Mapped[str] = mapped_column(
        String(5),
        default="08:00",
        nullable=False,
    )

    user = relationship(
        "User",
        back_populates="research_profile",
    )

    keywords = relationship(
        "ResearchKeyword",
        back_populates="profile",
        cascade="all, delete-orphan",
    )


class ResearchKeyword(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "research_keywords"

    profile_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("research_profiles.id", ondelete="CASCADE"),
        nullable=False,
    )

    keyword: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    category: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    is_excluded: Mapped[bool] = mapped_column(
        default=False,
        nullable=False,
    )

    profile = relationship(
        "ResearchProfile",
        back_populates="keywords",
    )
