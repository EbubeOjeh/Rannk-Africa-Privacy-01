"""ContactMessage — employer/recruiter → student relay.

Spec: "Contact Student" button on student profile keeps the student's email
private. Recruiter submits a message; the platform stores the message and
forwards it to the student's address via SMTP (when configured).
"""
from __future__ import annotations

import enum
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPKMixin

if TYPE_CHECKING:
    from app.models.student import Student


class ContactMessageStatus(str, enum.Enum):
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"
    BLOCKED = "blocked"


class ContactMessage(Base, UUIDPKMixin, TimestampMixin):
    __tablename__ = "contact_messages"

    student_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True
    )

    sender_name: Mapped[str] = mapped_column(String(160), nullable=False)
    sender_email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    sender_organization: Mapped[str | None] = mapped_column(String(200))
    sender_role: Mapped[str | None] = mapped_column(String(120))

    subject: Mapped[str] = mapped_column(String(200), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)

    status: Mapped[ContactMessageStatus] = mapped_column(
        Enum(ContactMessageStatus, name="contact_message_status"),
        default=ContactMessageStatus.PENDING,
        nullable=False,
    )
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    failure_reason: Mapped[str | None] = mapped_column(Text)

    student: Mapped["Student"] = relationship()
