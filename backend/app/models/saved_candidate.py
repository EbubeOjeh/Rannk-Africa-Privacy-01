"""SavedCandidate (PRS §12) — an employer bookmarks a promising student."""
from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPKMixin

if TYPE_CHECKING:
    from app.models.student import Student
    from app.models.user import User


class SavedCandidate(Base, UUIDPKMixin, TimestampMixin):
    __tablename__ = "saved_candidates"
    __table_args__ = (
        UniqueConstraint("employer_id", "student_id", name="uq_saved_candidate"),
    )

    employer_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    student_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True
    )
    notes: Mapped[str | None] = mapped_column(Text)

    employer: Mapped["User"] = relationship()
    student: Mapped["Student"] = relationship()
