"""OpportunityApplication — a student's internal application to an opportunity.

Students apply from the opportunity portal (gated on a complete profile); admins
review all applicants per opportunity. One application per (opportunity, student)
so re-applying is idempotent.
"""
from __future__ import annotations

import enum
from typing import TYPE_CHECKING

from sqlalchemy import Enum, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPKMixin

if TYPE_CHECKING:
    from app.models.opportunity import Opportunity
    from app.models.student import Student


class ApplicationStatus(str, enum.Enum):
    RECEIVED = "received"
    REVIEWED = "reviewed"
    SHORTLISTED = "shortlisted"
    REJECTED = "rejected"
    SELECTED = "selected"


class OpportunityApplication(Base, UUIDPKMixin, TimestampMixin):
    __tablename__ = "opportunity_applications"
    __table_args__ = (
        UniqueConstraint("opportunity_id", "student_id", name="uq_opportunity_application"),
    )

    opportunity_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("opportunities.id", ondelete="CASCADE"), nullable=False, index=True
    )
    student_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True
    )
    status: Mapped[ApplicationStatus] = mapped_column(
        Enum(ApplicationStatus, name="application_status"),
        default=ApplicationStatus.RECEIVED,
        nullable=False,
    )

    student: Mapped["Student"] = relationship()
    opportunity: Mapped["Opportunity"] = relationship()
