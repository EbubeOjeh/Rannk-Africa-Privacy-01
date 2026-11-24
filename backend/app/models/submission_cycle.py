"""SubmissionCycle — the per-year submission/review/publication window.

Cycle states follow the spec's lifecycle:
    DRAFT      — created by super-admin, not yet open
    OPEN       — schools may submit students
    REVIEW     — submission window closed, admin verifying
    PUBLISHED  — approved students are publicly visible on the leaderboard
    CLOSED     — cycle ended; scores LOCK and cannot be recomputed
"""
from __future__ import annotations

import enum
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, Enum, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPKMixin

if TYPE_CHECKING:
    from app.models.student import Student


class CycleStatus(str, enum.Enum):
    DRAFT = "draft"
    OPEN = "open"
    REVIEW = "review"
    PUBLISHED = "published"
    CLOSED = "closed"


class SubmissionCycle(Base, UUIDPKMixin, TimestampMixin):
    __tablename__ = "submission_cycles"

    name: Mapped[str] = mapped_column(String(120), nullable=False, unique=True)
    year: Mapped[int] = mapped_column(Integer, nullable=False, index=True)

    submission_opens_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    submission_closes_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    review_ends_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    status: Mapped[CycleStatus] = mapped_column(
        Enum(CycleStatus, name="cycle_status"),
        default=CycleStatus.DRAFT,
        nullable=False,
        index=True,
    )
    # Once the cycle CLOSES, is_locked flips true and scores can no longer be
    # recomputed for students in this cycle. Spec: "Scores lock once a
    # submission cycle closes."
    is_locked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    max_students_per_school: Mapped[int] = mapped_column(Integer, default=15, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)

    students: Mapped[list["Student"]] = relationship(back_populates="submission_cycle")
