"""OpportunityMatch (PRS §15) — cached AI compatibility score between a student
and an opportunity ("92% Match"), so the browse list doesn't re-call the model
on every page load.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Float, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPKMixin

if TYPE_CHECKING:
    from app.models.opportunity import Opportunity
    from app.models.student import Student


class OpportunityMatch(Base, UUIDPKMixin, TimestampMixin):
    __tablename__ = "opportunity_matches"
    __table_args__ = (
        UniqueConstraint("student_id", "opportunity_id", name="uq_opportunity_match"),
    )

    student_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True
    )
    opportunity_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("opportunities.id", ondelete="CASCADE"), nullable=False, index=True
    )
    score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)  # 0-100 "% match"
    reasoning: Mapped[str | None] = mapped_column(Text)
    engine: Mapped[str | None] = mapped_column(String(60))

    student: Mapped["Student"] = relationship()
    opportunity: Mapped["Opportunity"] = relationship()
