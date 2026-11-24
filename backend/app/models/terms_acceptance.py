"""TermsAcceptance (PRS §18) — record of a student's active agreement to the
Terms & Conditions before submitting their profile, kept for legal cover.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPKMixin

if TYPE_CHECKING:
    from app.models.student import Student
    from app.models.user import User

# Bump when the Terms & Conditions copy materially changes.
CURRENT_TERMS_VERSION = "2.1"


class TermsAcceptance(Base, UUIDPKMixin, TimestampMixin):
    __tablename__ = "terms_acceptances"

    user_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="SET NULL"), index=True
    )
    student_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("students.id", ondelete="SET NULL"), index=True
    )
    version: Mapped[str] = mapped_column(String(20), nullable=False)
    ip_address: Mapped[str | None] = mapped_column(String(60))
    user_agent: Mapped[str | None] = mapped_column(Text)
    accepted_text: Mapped[str | None] = mapped_column(Text)

    user: Mapped["User | None"] = relationship()
    student: Mapped["Student | None"] = relationship()
