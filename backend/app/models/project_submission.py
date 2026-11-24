"""ProjectSubmission — final-year project artifacts + AI-rubric scores (/40)."""
from __future__ import annotations

import enum
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import JSON, DateTime, Enum, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPKMixin

if TYPE_CHECKING:
    from app.models.student import Student


class ProjectStatus(str, enum.Enum):
    PENDING = "pending"          # Submitted, awaiting AI evaluation
    EVALUATED = "evaluated"      # AI has scored; awaiting human moderation if top-tier
    MODERATED = "moderated"      # Human reviewer signed off
    FAILED = "failed"            # AI / parsing error


class ProjectSubmission(Base, UUIDPKMixin, TimestampMixin):
    """A student project (PRS §5 — students may upload several). Each is scored
    on the four-category rubric; the student's best-scoring project drives the
    Projects & Innovation dimension (see Student.primary_project).

    Originality /10  ·  Technical Depth /10  ·  Problem Solving /10  ·  Innovation /10
    """

    __tablename__ = "project_submissions"

    student_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("students.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    title: Mapped[str] = mapped_column(String(240), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    problem_statement: Mapped[str | None] = mapped_column(Text)

    report_url: Mapped[str | None] = mapped_column(String(500))
    source_code_url: Mapped[str | None] = mapped_column(String(500))
    demo_video_url: Mapped[str | None] = mapped_column(String(500))

    originality: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    technical_depth: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    problem_solving: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    innovation: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    total_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    status: Mapped[ProjectStatus] = mapped_column(
        Enum(ProjectStatus, name="project_status"),
        default=ProjectStatus.PENDING,
        nullable=False,
    )

    ai_engine: Mapped[str | None] = mapped_column(String(40))  # e.g. "claude-opus-4-7"
    ai_reasoning: Mapped[dict | None] = mapped_column(JSON)
    moderator_notes: Mapped[str | None] = mapped_column(Text)

    evaluated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    moderated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    student: Mapped["Student"] = relationship(back_populates="projects")
