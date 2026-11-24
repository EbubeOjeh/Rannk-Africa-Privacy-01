"""EvaluationResult — output of the three-pipeline scoring engine."""
from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import JSON, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPKMixin

if TYPE_CHECKING:
    from app.models.student import Student


class EvaluationResult(Base, UUIDPKMixin, TimestampMixin):
    """One snapshot of a student's score across the three pipelines.

    Stored every time the engine runs so we have an audit trail of how a
    student's standing has changed over the cycle. ``final_score`` is on the
    /100 scale defined by the spec.
    """

    __tablename__ = "evaluation_results"

    student_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True
    )

    engine_version: Mapped[str] = mapped_column(String(20), default="v2", nullable=False)

    # Three pipelines (/40 + /40 + /20 = /100).
    academic_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    project_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    achievement_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    final_score: Mapped[float] = mapped_column(Float, nullable=False, index=True)

    # Auxiliary signals retained for transparency.
    normalized_gpa: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    consistency_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    # Legacy columns retained so older rows (and unit tests) keep validating.
    weighted_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    inflation_penalty: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    standardized_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    breakdown: Mapped[dict | None] = mapped_column(JSON)

    student: Mapped["Student"] = relationship(back_populates="evaluations")
