"""Competitions (PRS §5) — feeds the Competitions & Verified Achievements
dimension (10%), alongside verified Achievement rows.

Hackathons / Moot Court / Business Competitions / Debate Championships /
Music Awards / Innovation Challenges. Points scale with the result
(winner > finalist > participant).
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


class CompetitionType(str, enum.Enum):
    HACKATHON = "hackathon"
    MOOT_COURT = "moot_court"
    BUSINESS_COMPETITION = "business_competition"
    DEBATE = "debate"
    MUSIC_AWARD = "music_award"
    INNOVATION_CHALLENGE = "innovation_challenge"


class CompetitionResult(str, enum.Enum):
    WINNER = "winner"
    RUNNER_UP = "runner_up"
    FINALIST = "finalist"
    PARTICIPANT = "participant"


RESULT_POINTS: dict[CompetitionResult, int] = {
    CompetitionResult.WINNER: 5,
    CompetitionResult.RUNNER_UP: 4,
    CompetitionResult.FINALIST: 3,
    CompetitionResult.PARTICIPANT: 2,
}

COMPETITION_LABELS: dict[CompetitionType, str] = {
    CompetitionType.HACKATHON: "Hackathon",
    CompetitionType.MOOT_COURT: "Moot Court Competition",
    CompetitionType.BUSINESS_COMPETITION: "Business Competition",
    CompetitionType.DEBATE: "Debate Championship",
    CompetitionType.MUSIC_AWARD: "Music Award",
    CompetitionType.INNOVATION_CHALLENGE: "Innovation Challenge",
}


class Competition(Base, UUIDPKMixin, TimestampMixin):
    __tablename__ = "competitions"

    student_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True
    )

    type: Mapped[CompetitionType] = mapped_column(
        Enum(CompetitionType, name="competition_type"), nullable=False, index=True
    )
    result: Mapped[CompetitionResult] = mapped_column(
        Enum(CompetitionResult, name="competition_result"),
        default=CompetitionResult.PARTICIPANT,
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String(240), nullable=False)
    organizer: Mapped[str | None] = mapped_column(String(200))
    year: Mapped[int | None] = mapped_column(Integer)
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

    student: Mapped["Student"] = relationship(back_populates="competitions")
    verified_by: Mapped["User | None"] = relationship()
