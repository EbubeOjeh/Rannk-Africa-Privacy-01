"""Verification badges (PRS §14).

Badges are stored per-student (so they can be admin-granted or auto-awarded by
the verification engine) and rendered on the public profile + ranking rows to
help employers spot verified achievements at a glance.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPKMixin

if TYPE_CHECKING:
    from app.models.student import Student

# --- Badge catalog (key -> presentation) ------------------------------------
VERIFIED_STUDENT = "verified_student"
VERIFIED_RESEARCH = "verified_research"
INTERNSHIP_VERIFIED = "internship_verified"
VERIFIED_MUSIC = "verified_music_portfolio"
COMPETITION_WINNER = "competition_winner"
SCHOLARSHIP_RECIPIENT = "scholarship_recipient"

BADGE_CATALOG: list[dict[str, str]] = [
    {"key": VERIFIED_STUDENT, "label": "Verified Student", "emoji": "✅",
     "description": "Identity and enrolment verified by RankAfrica."},
    {"key": VERIFIED_RESEARCH, "label": "Verified Research", "emoji": "🏅",
     "description": "Has at least one verified research publication."},
    {"key": INTERNSHIP_VERIFIED, "label": "Internship Verified", "emoji": "💼",
     "description": "Has at least one verified internship/experience."},
    {"key": VERIFIED_MUSIC, "label": "Verified Music Portfolio", "emoji": "🎵",
     "description": "Music portfolio verified by RankAfrica."},
    {"key": COMPETITION_WINNER, "label": "Competition Winner", "emoji": "🏆",
     "description": "Won a verified competition."},
    {"key": SCHOLARSHIP_RECIPIENT, "label": "Scholarship Recipient", "emoji": "⭐",
     "description": "Verified scholarship recipient."},
]

BADGE_LABELS: dict[str, str] = {b["key"]: b["label"] for b in BADGE_CATALOG}
BADGE_EMOJI: dict[str, str] = {b["key"]: b["emoji"] for b in BADGE_CATALOG}
BADGE_KEYS: tuple[str, ...] = tuple(b["key"] for b in BADGE_CATALOG)


class StudentBadge(Base, UUIDPKMixin, TimestampMixin):
    __tablename__ = "student_badges"
    __table_args__ = (
        UniqueConstraint("student_id", "badge_key", name="uq_student_badge"),
    )

    student_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True
    )
    badge_key: Mapped[str] = mapped_column(String(60), nullable=False, index=True)
    # True when granted automatically by the verification engine vs. by an admin.
    is_auto: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    awarded_by_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="SET NULL")
    )

    student: Mapped["Student"] = relationship(back_populates="badges")
