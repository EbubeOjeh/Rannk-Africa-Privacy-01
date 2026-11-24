"""Achievement records — six types, each with fixed point value and evidence.

Point values are taken straight from the spec:

    Internship              3 pts
    Hackathon Participation 2 pts
    Hackathon Win           5 pts
    Leadership Role         5 pts
    Publication             6 pts
    Startup Built           8 pts

The total achievement score for a student is hard-capped at 20 points
regardless of accumulated total — enforced in the evaluation engine.
"""
from __future__ import annotations

import enum
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPKMixin

if TYPE_CHECKING:
    from app.models.student import Student
    from app.models.user import User


class AchievementType(str, enum.Enum):
    INTERNSHIP = "internship"
    HACKATHON_PARTICIPATION = "hackathon_participation"
    HACKATHON_WIN = "hackathon_win"
    LEADERSHIP_ROLE = "leadership_role"
    PUBLICATION = "publication"
    STARTUP_BUILT = "startup_built"
    # PRS §5 "Verified Achievements": awards, certifications, scholarships,
    # grants, fellowships, national recognition.
    AWARD = "award"
    CERTIFICATION = "certification"
    SCHOLARSHIP = "scholarship"
    GRANT = "grant"
    FELLOWSHIP = "fellowship"
    NATIONAL_RECOGNITION = "national_recognition"


ACHIEVEMENT_POINTS: dict[AchievementType, int] = {
    AchievementType.INTERNSHIP: 3,
    AchievementType.HACKATHON_PARTICIPATION: 2,
    AchievementType.HACKATHON_WIN: 5,
    AchievementType.LEADERSHIP_ROLE: 5,
    AchievementType.PUBLICATION: 6,
    AchievementType.STARTUP_BUILT: 8,
    AchievementType.AWARD: 3,
    AchievementType.CERTIFICATION: 2,
    AchievementType.SCHOLARSHIP: 4,
    AchievementType.GRANT: 4,
    AchievementType.FELLOWSHIP: 5,
    AchievementType.NATIONAL_RECOGNITION: 5,
}

ACHIEVEMENT_CAP = 20

ACHIEVEMENT_LABELS: dict[AchievementType, str] = {
    AchievementType.INTERNSHIP: "Internship",
    AchievementType.HACKATHON_PARTICIPATION: "Hackathon Participation",
    AchievementType.HACKATHON_WIN: "Hackathon Win",
    AchievementType.LEADERSHIP_ROLE: "Leadership Role",
    AchievementType.PUBLICATION: "Publication",
    AchievementType.STARTUP_BUILT: "Startup Built",
    AchievementType.AWARD: "Award",
    AchievementType.CERTIFICATION: "Certification",
    AchievementType.SCHOLARSHIP: "Scholarship",
    AchievementType.GRANT: "Grant",
    AchievementType.FELLOWSHIP: "Fellowship",
    AchievementType.NATIONAL_RECOGNITION: "National Recognition",
}

# Which /100 dimension each achievement type contributes to in the v2.0 engine.
# This lets legacy Achievement rows feed the right component score.
ACHIEVEMENT_DIMENSION: dict[AchievementType, str] = {
    AchievementType.PUBLICATION: "research",
    AchievementType.INTERNSHIP: "experience",
    AchievementType.STARTUP_BUILT: "experience",
    AchievementType.LEADERSHIP_ROLE: "leadership",
    AchievementType.HACKATHON_PARTICIPATION: "competition",
    AchievementType.HACKATHON_WIN: "competition",
    AchievementType.AWARD: "competition",
    AchievementType.CERTIFICATION: "competition",
    AchievementType.SCHOLARSHIP: "competition",
    AchievementType.GRANT: "competition",
    AchievementType.FELLOWSHIP: "competition",
    AchievementType.NATIONAL_RECOGNITION: "competition",
}


class VerificationStatus(str, enum.Enum):
    UNVERIFIED = "unverified"
    VERIFIED = "verified"
    REJECTED = "rejected"


class Achievement(Base, UUIDPKMixin, TimestampMixin):
    __tablename__ = "achievements"

    student_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("students.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    type: Mapped[AchievementType] = mapped_column(
        Enum(AchievementType, name="achievement_type"), nullable=False, index=True
    )
    points: Mapped[int] = mapped_column(Integer, nullable=False)

    title: Mapped[str] = mapped_column(String(240), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    link: Mapped[str | None] = mapped_column(String(500))            # public artifact (DOI, repo, etc.)
    evidence_url: Mapped[str | None] = mapped_column(String(500))    # uploaded certificate/proof

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

    student: Mapped["Student"] = relationship(back_populates="achievements")
    verified_by: Mapped["User | None"] = relationship()
