
import enum
import uuid
from datetime import date

from sqlalchemy import (
    String, Text, Integer, Date, ForeignKey,
    JSON, Enum, UniqueConstraint
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, UUIDMixin, TimestampMixin


class PaperStatus(str, enum.Enum):
    NEW = "new"
    SAVED = "saved"
    DISMISSED = "dismissed"
    READ = "read"


class Paper(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "papers"

    doi: Mapped[str | None] = mapped_column(
        String(255),
        unique=True,
        nullable=True,
    )

    title: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    abstract: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    publication_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    authors: Mapped[list] = mapped_column(
        JSON,
        default=list,
        nullable=False,
    )

    venue: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    citation_count: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    sources = relationship(
        "PaperSource",
        back_populates="paper",
        cascade="all, delete-orphan",
    )

    user_papers = relationship(
        "UserPaper",
        back_populates="paper",
        cascade="all, delete-orphan",
    )


class PaperSource(UUIDMixin, Base):
    __tablename__ = "paper_sources"

    paper_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("papers.id", ondelete="CASCADE"),
        nullable=False,
    )

    source: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    source_id: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    source_url: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    __table_args__ = (
        UniqueConstraint(
            "source",
            "source_id",
            name="uq_paper_source_id",
        ),
    )

    paper = relationship("Paper", back_populates="sources")


class UserPaper(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "user_papers"

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    paper_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("papers.id", ondelete="CASCADE"),
        nullable=False,
    )

    relevance_score: Mapped[float | None] = mapped_column(
        nullable=True,
    )

    status: Mapped[PaperStatus] = mapped_column(
        Enum(PaperStatus, native_enum=False),
        default=PaperStatus.NEW,
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "paper_id",
            name="uq_user_paper",
        ),
    )

    user = relationship("User", back_populates="user_papers")
    paper = relationship("Paper", back_populates="user_papers")
