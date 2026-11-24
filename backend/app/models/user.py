"""User model + role enum."""
from __future__ import annotations

import enum
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, String, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPKMixin

if TYPE_CHECKING:
    from app.models.employer_profile import EmployerProfile
    from app.models.role import Role
    from app.models.university import University


class UserRole(str, enum.Enum):
    SUPER_ADMIN = "super_admin"           # RankAfrica internal team
    SCHOOL_ADMIN = "school_admin"         # University representative (a.k.a. school admin in the spec)
    UNIVERSITY_ADMIN = "university_admin" # Legacy alias of SCHOOL_ADMIN — kept for backwards compat
    STUDENT = "student"                   # Listed on the leaderboard; can sign in to claim/edit profile
    EMPLOYER = "employer"                 # Recruiter / employer — must be approved to view contact info
    EVALUATOR = "evaluator"               # Internal moderator who reviews AI project scores
    EMPLOYEE = "employee"                 # RankAfrica company staff — abilities come from their company Role


class UserApprovalStatus(str, enum.Enum):
    """Approval state for recruiter/employer accounts (others default APPROVED)."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


SCHOOL_ADMIN_ROLES: tuple[UserRole, ...] = (UserRole.SCHOOL_ADMIN, UserRole.UNIVERSITY_ADMIN)


class User(Base, UUIDPKMixin, TimestampMixin):
    __tablename__ = "users"

    name: Mapped[str] = mapped_column(String(160), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, name="user_role"), default=UserRole.SCHOOL_ADMIN, nullable=False
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_email_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Recruiter/employer approval state (everyone else defaults APPROVED).
    approval_status: Mapped[UserApprovalStatus] = mapped_column(
        Enum(UserApprovalStatus, name="user_approval_status"),
        default=UserApprovalStatus.APPROVED,
        server_default=text("'APPROVED'"),
        nullable=False,
    )

    # Force a password change on next login (seeded staff accounts start True).
    must_change_password: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Test/dummy accounts created by the CEO/admin to exercise the flows. They
    # are auto-deleted 20 days after creation (see test_account_service). The
    # 20-day window is computed from ``created_at``; no extra timestamp needed.
    is_test_account: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default=text("false"), nullable=False
    )
    # Profile picture (Supabase Storage URL) + job-title label for staff.
    avatar_url: Mapped[str | None] = mapped_column(String(500))
    title: Mapped[str | None] = mapped_column(String(120))

    # For SCHOOL_ADMIN / UNIVERSITY_ADMIN — the institution they represent.
    university_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("universities.id", ondelete="SET NULL"), nullable=True
    )

    # For EMPLOYEE accounts — the company role granting their permissions.
    company_role_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("roles.id", ondelete="SET NULL"), nullable=True
    )

    # For EMPLOYER accounts (phase 2).
    organization: Mapped[str | None] = mapped_column(String(200))

    # Suspension (PRS §13 — admin can suspend users). is_active gates login;
    # these record the why/when for the audit trail.
    suspension_reason: Mapped[str | None] = mapped_column(String(500))
    suspended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    university: Mapped["University | None"] = relationship(back_populates="admins")
    company_role: Mapped["Role | None"] = relationship(back_populates="members")
    employer_profile: Mapped["EmployerProfile | None"] = relationship(
        back_populates="user", cascade="all,delete-orphan", uselist=False,
        foreign_keys="EmployerProfile.user_id",
    )
