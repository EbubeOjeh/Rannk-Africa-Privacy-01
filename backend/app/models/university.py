"""University model."""
from __future__ import annotations

import enum
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPKMixin

if TYPE_CHECKING:
    from app.models.department import Department
    from app.models.faculty import Faculty
    from app.models.student import Student
    from app.models.user import User


class SchoolApprovalStatus(str, enum.Enum):
    """Lifecycle of a school's registration on RankAfrica.

        PENDING  — submitted via /auth/register-school, awaiting Super Admin review
        APPROVED — Super Admin approved; school admin may upload students etc.
        REJECTED — Super Admin rejected (with reason); admin can re-apply
    """
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class University(Base, UUIDPKMixin, TimestampMixin):
    __tablename__ = "universities"

    name: Mapped[str] = mapped_column(String(200), unique=True, nullable=False, index=True)
    slug: Mapped[str] = mapped_column(String(220), unique=True, nullable=False, index=True)
    short_name: Mapped[str | None] = mapped_column(String(50))
    country: Mapped[str] = mapped_column(String(80), default="Nigeria", nullable=False, index=True)
    state: Mapped[str | None] = mapped_column(String(80), index=True)
    city: Mapped[str | None] = mapped_column(String(120))
    website: Mapped[str | None] = mapped_column(String(255))
    logo_url: Mapped[str | None] = mapped_column(String(500))
    description: Mapped[str | None] = mapped_column(Text)

    # Apex domain extracted from the school admin's institutional email
    # (e.g. "babcock.edu.ng" from "admin@student.babcock.edu.ng"). Used to
    # detect duplicate registrations.
    domain: Mapped[str | None] = mapped_column(String(120), unique=True, index=True)

    grading_system: Mapped[str] = mapped_column(String(50), default="5_point", nullable=False)
    accreditation_type: Mapped[str | None] = mapped_column(String(80))
    # WES-style engine reads this to pick the right class-of-degree table:
    #   "university"  -> First Class / 2:1 / 2:2 / Third / Pass
    #   "polytechnic" -> Distinction / Upper Credit / Lower Credit / Pass
    institution_type: Mapped[str] = mapped_column(
        String(20), default="university", nullable=False, index=True
    )
    tier: Mapped[int] = mapped_column(Integer, default=3, nullable=False)

    approval_status: Mapped[SchoolApprovalStatus] = mapped_column(
        Enum(SchoolApprovalStatus, name="school_approval_status"),
        default=SchoolApprovalStatus.PENDING,
        nullable=False,
        index=True,
    )
    approval_notes: Mapped[str | None] = mapped_column(String(500))
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    # Plain UUID column (no FK) — University ↔ User would otherwise form a
    # cycle (User.university_id <-> University.approved_by_id) that SQLite
    # cannot resolve at DROP-time. We join manually when needed.
    approved_by_id: Mapped[str | None] = mapped_column(String(36))

    avg_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    top_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    elite_student_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    student_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    overall_rank: Mapped[int | None] = mapped_column(Integer, index=True)

    admins: Mapped[list["User"]] = relationship(
        back_populates="university", foreign_keys="User.university_id"
    )
    students: Mapped[list["Student"]] = relationship(back_populates="university", cascade="all,delete-orphan")
    departments: Mapped[list["Department"]] = relationship(back_populates="university", cascade="all,delete-orphan")
    faculties: Mapped[list["Faculty"]] = relationship(back_populates="university", cascade="all,delete-orphan")
