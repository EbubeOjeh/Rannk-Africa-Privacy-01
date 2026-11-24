"""Research & Publications (PRS §5) — feeds the Research dimension (15%).

Journal Publications / Conference Papers / Undergraduate Research /
Research Assistantships / Book Chapters. Only VERIFIED items count at full
weight in the scorer; unverified items count at a provisional factor so
self-registered students see an indicative score before review.
"""
from __future__ import annotations

import enum
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPKMixin
from app.models.achievement import VerificationStatus

if TYPE_CHECKING:
    from app.models.student import Student
    from app.models.user import User


class ResearchType(str, enum.Enum):
    JOURNAL_PUBLICATION = "journal_publication"
    CONFERENCE_PAPER = "conference_paper"
    UNDERGRADUATE_RESEARCH = "undergraduate_research"
    RESEARCH_ASSISTANTSHIP = "research_assistantship"
    BOOK_CHAPTER = "book_chapter"


RESEARCH_POINTS: dict[ResearchType, int] = {
    ResearchType.JOURNAL_PUBLICATION: 6,
    ResearchType.CONFERENCE_PAPER: 4,
    ResearchType.BOOK_CHAPTER: 5,
    ResearchType.UNDERGRADUATE_RESEARCH: 2,
    ResearchType.RESEARCH_ASSISTANTSHIP: 2,
}

RESEARCH_LABELS: dict[ResearchType, str] = {
    ResearchType.JOURNAL_PUBLICATION: "Journal Publication",
    ResearchType.CONFERENCE_PAPER: "Conference Paper",
    ResearchType.BOOK_CHAPTER: "Book Chapter",
    ResearchType.UNDERGRADUATE_RESEARCH: "Undergraduate Research",
    ResearchType.RESEARCH_ASSISTANTSHIP: "Research Assistantship",
}


class ResearchPublication(Base, UUIDPKMixin, TimestampMixin):
    __tablename__ = "research_publications"

    student_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True
    )

    type: Mapped[ResearchType] = mapped_column(
        Enum(ResearchType, name="research_type"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    venue: Mapped[str | None] = mapped_column(String(240))   # journal / conference name
    year: Mapped[int | None] = mapped_column(Integer)
    citations: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    doi: Mapped[str | None] = mapped_column(String(200))
    link: Mapped[str | None] = mapped_column(String(500))
    description: Mapped[str | None] = mapped_column(Text)
    evidence_url: Mapped[str | None] = mapped_column(String(500))

    # Optional AI-assessed quality (0-1) used to weight the item; null = unscored.
    ai_quality: Mapped[float | None] = mapped_column(Float)

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

    student: Mapped["Student"] = relationship(back_populates="research_items")
    verified_by: Mapped["User | None"] = relationship()
