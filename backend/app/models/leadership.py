"""Leadership & Extracurricular activities (PRS §6) — the Leadership dimension
(10%): student leadership, volunteer work, community impact, professional
organizations.
"""
from __future__ import annotations

import enum
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPKMixin
from app.models.achievement import VerificationStatus

if TYPE_CHECKING:
    from app.models.student import Student
    from app.models.user import User


class LeadershipType(str, enum.Enum):
    STUDENT_LEADERSHIP = "student_leadership"
    VOLUNTEER_WORK = "volunteer_work"
    COMMUNITY_IMPACT = "community_impact"
    PROFESSIONAL_ORG = "professional_org"


LEADERSHIP_POINTS: dict[LeadershipType, int] = {
    LeadershipType.STUDENT_LEADERSHIP: 4,
    LeadershipType.COMMUNITY_IMPACT: 3,
    LeadershipType.PROFESSIONAL_ORG: 2,
    LeadershipType.VOLUNTEER_WORK: 2,
}

LEADERSHIP_LABELS: dict[LeadershipType, str] = {
    LeadershipType.STUDENT_LEADERSHIP: "Student Leadership",
    LeadershipType.VOLUNTEER_WORK: "Volunteer Work",
    LeadershipType.COMMUNITY_IMPACT: "Community Impact",
    LeadershipType.PROFESSIONAL_ORG: "Professional Organization",
}


class LeadershipActivity(Base, UUIDPKMixin, TimestampMixin):
    __tablename__ = "leadership_activities"

    student_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True
    )

    type: Mapped[LeadershipType] = mapped_column(
        Enum(LeadershipType, name="leadership_type"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(240), nullable=False)
    organization: Mapped[str | None] = mapped_column(String(200))
    role_title: Mapped[str | None] = mapped_column(String(200))
    start_date: Mapped[str | None] = mapped_column(String(40))
    end_date: Mapped[str | None] = mapped_column(String(40))
    description: Mapped[str | None] = mapped_column(Text)
    link: Mapped[str | None] = mapped_column(String(500))
    evidence_url: Mapped[str | None] = mapped_column(String(500))

    verification_status: Mapped[VerificationStatus] = mapped_column(
        Enum(VerificationStatus, name="verification_status"),
        default=VerificationStatus.UNVERIFIED,
        nullable=False,
    )
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    verified_by_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="SET NULL")
    )
    rejection_reason: Mapped[str | None] = mapped_column(Text)

    student: Mapped["Student"] = relationship(back_populates="leadership_items")
    verified_by: Mapped["User | None"] = relationship()
