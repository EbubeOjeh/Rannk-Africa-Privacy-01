"""Student model — academic profile, 3-pipeline scoring, approval state."""
from __future__ import annotations

import enum
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import JSON, Boolean, DateTime, Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPKMixin

if TYPE_CHECKING:
    from app.models.achievement import Achievement
    from app.models.ai_flag import AIFlag
    from app.models.badge import StudentBadge
    from app.models.competition import Competition
    from app.models.department import Department
    from app.models.evaluation import EvaluationResult
    from app.models.experience import Experience
    from app.models.field import Field
    from app.models.leadership import LeadershipActivity
    from app.models.project_submission import ProjectSubmission
    from app.models.research import ResearchPublication
    from app.models.submission_cycle import SubmissionCycle
    from app.models.university import University
    from app.models.user import User


class ApprovalStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class Student(Base, UUIDPKMixin, TimestampMixin):
    __tablename__ = "students"

    full_name: Mapped[str] = mapped_column(String(180), nullable=False, index=True)
    email: Mapped[str | None] = mapped_column(String(255), index=True)
    phone_number: Mapped[str | None] = mapped_column(String(40))
    linkedin_url: Mapped[str | None] = mapped_column(String(500))
    matric_number: Mapped[str | None] = mapped_column(String(80), index=True)
    gender: Mapped[str | None] = mapped_column(String(20))
    avatar_url: Mapped[str | None] = mapped_column(String(500))
    academic_level: Mapped[int | None] = mapped_column(Integer)
    year_of_study: Mapped[int | None] = mapped_column(Integer)  # PRS §5 "Year of Study"
    bio: Mapped[str | None] = mapped_column(String(1600))  # ~200 words

    # Free-text "Achievements & Profile Assessment" — for non-Technology/Music
    # fields, the student describes their accomplishments here and the AI scores
    # it out of /60 (stored in profile_score). Students are told this text is
    # used in their evaluation.
    profile_statement: Mapped[str | None] = mapped_column(Text)

    # PRS §5 — academic identity supplied by the student at registration.
    course: Mapped[str | None] = mapped_column(String(200))   # degree/course → maps to field
    faculty: Mapped[str | None] = mapped_column(String(200))

    # PRS §5 — additional profile info + professional links.
    skills: Mapped[list | None] = mapped_column(JSON)         # list[str]
    languages: Mapped[list | None] = mapped_column(JSON)      # list[str]
    resume_url: Mapped[str | None] = mapped_column(String(500))
    # Student-uploaded UNOFFICIAL transcript / semester results (final-year
    # students rarely have an official transcript yet).
    transcript_url: Mapped[str | None] = mapped_column(String(500))
    portfolio_url: Mapped[str | None] = mapped_column(String(500))
    github_url: Mapped[str | None] = mapped_column(String(500))
    behance_url: Mapped[str | None] = mapped_column(String(500))
    google_scholar_url: Mapped[str | None] = mapped_column(String(500))
    music_url: Mapped[str | None] = mapped_column(String(500))   # Spotify/Apple/YouTube
    whatsapp_number: Mapped[str | None] = mapped_column(String(40))

    # Hybrid model: links a self-registered student to their login + records
    # that they signed up themselves (vs. being uploaded by a school admin).
    user_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="SET NULL"), index=True
    )
    is_self_registered: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    terms_accepted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    # GPA on the school's native scale + the normalized 4.0-scale value used
    # by the academic pipeline. Spec: "CGPA is normalised to a 4.0 scale".
    raw_gpa: Mapped[float | None] = mapped_column(Float)
    raw_cgpa: Mapped[float | None] = mapped_column(Float)
    gpa_scale: Mapped[float] = mapped_column(Float, default=5.0, nullable=False)
    normalized_cgpa: Mapped[float | None] = mapped_column(Float)
    # WES-style engine outputs (also surfaced on the public profile):
    standardized_gpa_4: Mapped[float | None] = mapped_column(Float)
    class_of_degree: Mapped[str | None] = mapped_column(String(40))
    credits_earned: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Component scores. Per-field model (engine v3):
    #   Technology / Music : Academic 40 + Project 40 + Achievements 20 = /100
    #   All other fields   : Academic 40 + Profile Assessment 60        = /100
    # (research/leadership/experience/competition kept for back-compat; not part
    # of the v3 /100 and left at 0.)
    academic_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    project_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    achievement_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    # AI "Achievements & Profile Assessment" /60 for non-Technology/Music fields.
    profile_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    research_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    leadership_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    experience_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    competition_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    final_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False, index=True)
    # Mirror of final_score retained for backwards-compatibility with the
    # original /30 standardized_score column used by older clients.
    standardized_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False, index=True)
    consistency_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    overall_rank: Mapped[int | None] = mapped_column(Integer, index=True)
    field_rank: Mapped[int | None] = mapped_column(Integer)
    university_rank: Mapped[int | None] = mapped_column(Integer)
    department_rank: Mapped[int | None] = mapped_column(Integer)

    # Cycle + approval lifecycle.
    submission_cycle_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("submission_cycles.id", ondelete="SET NULL"), index=True
    )
    approval_status: Mapped[ApprovalStatus] = mapped_column(
        Enum(ApprovalStatus, name="approval_status"),
        default=ApprovalStatus.PENDING,
        nullable=False,
        index=True,
    )
    is_publicly_visible: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    approval_notes: Mapped[str | None] = mapped_column(String(500))
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    approved_by_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="SET NULL")
    )

    university_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("universities.id", ondelete="CASCADE"), nullable=False, index=True
    )
    department_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("departments.id", ondelete="SET NULL"), index=True
    )
    field_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("fields.id", ondelete="SET NULL"), index=True
    )

    university: Mapped["University"] = relationship(back_populates="students")
    department: Mapped["Department | None"] = relationship(back_populates="students")
    field: Mapped["Field | None"] = relationship(back_populates="students")
    submission_cycle: Mapped["SubmissionCycle | None"] = relationship(back_populates="students")
    evaluations: Mapped[list["EvaluationResult"]] = relationship(
        back_populates="student", cascade="all,delete-orphan"
    )
    projects: Mapped[list["ProjectSubmission"]] = relationship(
        back_populates="student",
        cascade="all,delete-orphan",
        order_by="ProjectSubmission.total_score.desc()",
    )
    achievements: Mapped[list["Achievement"]] = relationship(
        back_populates="student", cascade="all,delete-orphan"
    )
    research_items: Mapped[list["ResearchPublication"]] = relationship(
        back_populates="student", cascade="all,delete-orphan"
    )
    experiences: Mapped[list["Experience"]] = relationship(
        back_populates="student", cascade="all,delete-orphan"
    )
    competitions: Mapped[list["Competition"]] = relationship(
        back_populates="student", cascade="all,delete-orphan"
    )
    leadership_items: Mapped[list["LeadershipActivity"]] = relationship(
        back_populates="student", cascade="all,delete-orphan"
    )
    badges: Mapped[list["StudentBadge"]] = relationship(
        back_populates="student", cascade="all,delete-orphan"
    )
    ai_flags: Mapped[list["AIFlag"]] = relationship(
        back_populates="student", cascade="all,delete-orphan"
    )
    account: Mapped["User | None"] = relationship(foreign_keys="Student.user_id")

    @property
    def primary_project(self) -> "ProjectSubmission | None":
        """The best-scoring project — drives the Projects & Innovation score."""
        return self.projects[0] if self.projects else None

    @property
    def field_slug(self) -> str | None:
        """Convenience for serializers/frontend field-model branching."""
        return self.field.slug if self.field else None
