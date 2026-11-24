"""AIFlag (PRS §7, §13) — integrity flags raised by the AI verification suite
(fake transcripts, edited certificates, duplicate publications, plagiarised
projects, suspicious claims, duplicate accounts). Flagged items are held for
manual review before they affect rankings.
"""
from __future__ import annotations

import enum
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import JSON, DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPKMixin

if TYPE_CHECKING:
    from app.models.student import Student
    from app.models.user import User


class FlagType(str, enum.Enum):
    FAKE_TRANSCRIPT = "fake_transcript"
    EDITED_CERTIFICATE = "edited_certificate"
    DUPLICATE_PUBLICATION = "duplicate_publication"
    PLAGIARIZED_PROJECT = "plagiarized_project"
    SUSPICIOUS_CLAIM = "suspicious_claim"
    DUPLICATE_ACCOUNT = "duplicate_account"


class FlagSeverity(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class FlagStatus(str, enum.Enum):
    OPEN = "open"
    CONFIRMED = "confirmed"
    DISMISSED = "dismissed"


FLAG_LABELS: dict[FlagType, str] = {
    FlagType.FAKE_TRANSCRIPT: "Possible fake transcript",
    FlagType.EDITED_CERTIFICATE: "Possible edited certificate",
    FlagType.DUPLICATE_PUBLICATION: "Duplicate publication",
    FlagType.PLAGIARIZED_PROJECT: "Possible plagiarised project",
    FlagType.SUSPICIOUS_CLAIM: "Suspicious claim",
    FlagType.DUPLICATE_ACCOUNT: "Possible duplicate account",
}


class AIFlag(Base, UUIDPKMixin, TimestampMixin):
    __tablename__ = "ai_flags"

    student_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("students.id", ondelete="CASCADE"), index=True
    )
    # The flagged record (e.g. ("transcript", <id>), ("project", <id>)).
    entity_type: Mapped[str | None] = mapped_column(String(40))
    entity_id: Mapped[str | None] = mapped_column(String(36))

    flag_type: Mapped[FlagType] = mapped_column(
        Enum(FlagType, name="ai_flag_type"), nullable=False, index=True
    )
    severity: Mapped[FlagSeverity] = mapped_column(
        Enum(FlagSeverity, name="ai_flag_severity"),
        default=FlagSeverity.MEDIUM,
        nullable=False,
    )
    status: Mapped[FlagStatus] = mapped_column(
        Enum(FlagStatus, name="ai_flag_status"),
        default=FlagStatus.OPEN,
        nullable=False,
        index=True,
    )
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    details: Mapped[dict | None] = mapped_column(JSON)
    ai_engine: Mapped[str | None] = mapped_column(String(60))

    reviewed_by_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="SET NULL")
    )
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    review_notes: Mapped[str | None] = mapped_column(Text)

    student: Mapped["Student | None"] = relationship(back_populates="ai_flags")
    reviewed_by: Mapped["User | None"] = relationship()
