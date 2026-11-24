"""Experience (PRS §5) — feeds the Internships & Experience dimension (10%).

Internships / Volunteer Experience / Startups / Businesses / Employment.
Scored on organization quality, duration and relevance (the spec's criteria).
"""
from __future__ import annotations

import enum
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPKMixin
from app.models.achievement import VerificationStatus

if TYPE_CHECKING:
    from app.models.student import Student
    from app.models.user import User


class ExperienceType(str, enum.Enum):
    INTERNSHIP = "internship"
    VOLUNTEER = "volunteer"
    STARTUP = "startup"
    BUSINESS = "business"
    EMPLOYMENT = "employment"


EXPERIENCE_POINTS: dict[ExperienceType, int] = {
    ExperienceType.INTERNSHIP: 3,
    ExperienceType.EMPLOYMENT: 3,
    ExperienceType.STARTUP: 5,
    ExperienceType.BUSINESS: 4,
    ExperienceType.VOLUNTEER: 2,
}

EXPERIENCE_LABELS: dict[ExperienceType, str] = {
    ExperienceType.INTERNSHIP: "Internship",
    ExperienceType.VOLUNTEER: "Volunteer Experience",
    ExperienceType.STARTUP: "Startup",
    ExperienceType.BUSINESS: "Business",
    ExperienceType.EMPLOYMENT: "Employment",
}


class Experience(Base, UUIDPKMixin, TimestampMixin):
    __tablename__ = "experiences"

    student_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True
    )

    type: Mapped[ExperienceType] = mapped_column(
        Enum(ExperienceType, name="experience_type"), nullable=False, index=True
    )
    organization: Mapped[str] = mapped_column(String(200), nullable=False)
    role_title: Mapped[str | None] = mapped_column(String(200))
    location: Mapped[str | None] = mapped_column(String(160))
    # Stored as free text ("Jun 2024", "Summer 2023") so forms stay forgiving.
    start_date: Mapped[str | None] = mapped_column(String(40))
    end_date: Mapped[str | None] = mapped_column(String(40))
    is_current: Mapped[bool] = mapped_column(default=False, nullable=False)
    duration_months: Mapped[int | None] = mapped_column(Integer)
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

    student: Mapped["Student"] = relationship(back_populates="experiences")
    verified_by: Mapped["User | None"] = relationship()
