"""Opportunity (PRS §12, §15) — internships, graduate jobs, scholarships,
research positions, competitions and leadership programs posted by approved
employers (or by admins) and browsable by students with an AI "% match".
"""
from __future__ import annotations

import enum
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPKMixin

if TYPE_CHECKING:
    from app.models.field import Field
    from app.models.user import User


class OpportunityType(str, enum.Enum):
    INTERNSHIP = "internship"
    GRADUATE_JOB = "graduate_job"
    SCHOLARSHIP = "scholarship"
    RESEARCH = "research"
    COMPETITION = "competition"
    LEADERSHIP_PROGRAM = "leadership_program"


OPPORTUNITY_LABELS: dict[OpportunityType, str] = {
    OpportunityType.INTERNSHIP: "Internship",
    OpportunityType.GRADUATE_JOB: "Graduate Job",
    OpportunityType.SCHOLARSHIP: "Scholarship",
    OpportunityType.RESEARCH: "Research Position",
    OpportunityType.COMPETITION: "Competition",
    OpportunityType.LEADERSHIP_PROGRAM: "Leadership Program",
}


class Opportunity(Base, UUIDPKMixin, TimestampMixin):
    __tablename__ = "opportunities"

    posted_by_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="SET NULL"), index=True
    )
    organization: Mapped[str | None] = mapped_column(String(200))

    type: Mapped[OpportunityType] = mapped_column(
        Enum(OpportunityType, name="opportunity_type"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(240), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    location: Mapped[str | None] = mapped_column(String(160))
    requirements: Mapped[str | None] = mapped_column(Text)
    apply_url: Mapped[str | None] = mapped_column(String(500))
    deadline: Mapped[str | None] = mapped_column(String(40))

    # Targeting / filter hints used by the AI matcher + student browse filters.
    field_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("fields.id", ondelete="SET NULL"), index=True
    )
    min_gpa: Mapped[float | None] = mapped_column(Float)
    min_score: Mapped[float | None] = mapped_column(Float)
    graduation_year: Mapped[int | None] = mapped_column(Integer)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    is_featured: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    posted_by: Mapped["User | None"] = relationship()
    field: Mapped["Field | None"] = relationship()
