
import enum
import uuid

# from sqlalchemy import ForeignKey, Enum, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, UUIDMixin, TimestampMixin
from sqlalchemy import ForeignKey, Enum, UniqueConstraint, String

class FeedbackType(str, enum.Enum):
    RELEVANT = "relevant"
    NOT_RELEVANT = "not_relevant"
    INTERESTING = "interesting"
    ALREADY_KNOWN = "already_known"


class UserFeedback(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "user_feedback"

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    paper_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("papers.id", ondelete="CASCADE"),
        nullable=False,
    )

    feedback_type: Mapped[FeedbackType] = mapped_column(
        Enum(FeedbackType, native_enum=False),
        nullable=False,
    )
    matched_interest: Mapped[str | None] = mapped_column(
        String(200),
        nullable=True,
    )
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "paper_id",
            name="uq_user_paper_feedback",
        ),
    )
