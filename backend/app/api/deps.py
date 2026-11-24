"""Shared FastAPI dependencies — DB session, current user, RBAC.

Role hierarchy in this app:
    SUPER_ADMIN  > SCHOOL_ADMIN / UNIVERSITY_ADMIN  > EVALUATOR / STUDENT / EMPLOYER

``UNIVERSITY_ADMIN`` is the legacy enum value for what the spec calls "School
Admin". Both names map to the same set of capabilities — see SCHOOL_ADMIN_ROLES.
"""
from __future__ import annotations

from fastapi import Depends, Header
from sqlalchemy.orm import Session

from app.core.exceptions import ForbiddenError, NotFoundError, UnauthorizedError
from app.core.permissions import UPLOAD_TRANSCRIPTS, get_permissions, has_permission
from app.core.security import decode_token
from app.db.session import get_db
from app.models.student import Student
from app.models.university import SchoolApprovalStatus, University
from app.models.user import SCHOOL_ADMIN_ROLES, User, UserApprovalStatus, UserRole


def get_current_user(
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> User:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise UnauthorizedError("Missing bearer token.")
    token = authorization.split(" ", 1)[1].strip()
    payload = decode_token(token)
    if not payload or payload.get("type") != "access":
        raise UnauthorizedError("Invalid or expired token.")
    user = db.query(User).filter(User.id == payload["sub"]).first()
    if not user or not user.is_active:
        raise UnauthorizedError("Account unavailable.")
    return user


def get_current_user_optional(
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> User | None:
    """Like get_current_user but returns None instead of raising — for public
    endpoints that reveal more to a signed-in (and approved) viewer."""
    if not authorization or not authorization.lower().startswith("bearer "):
        return None
    payload = decode_token(authorization.split(" ", 1)[1].strip())
    if not payload or payload.get("type") != "access":
        return None
    user = db.query(User).filter(User.id == payload["sub"]).first()
    if not user or not user.is_active:
        return None
    return user


# Internal roles that always see student contact details.
_CONTACT_TRUSTED_ROLES = (
    UserRole.SUPER_ADMIN,
    UserRole.EMPLOYEE,
    UserRole.EVALUATOR,
    *SCHOOL_ADMIN_ROLES,
)


def can_view_contact(user: User | None) -> bool:
    """Who may see a student's private contact details / send them a message:
    internal staff, and recruiters whose account has been APPROVED."""
    if user is None:
        return False
    if user.role in _CONTACT_TRUSTED_ROLES:
        return True
    if user.role == UserRole.EMPLOYER:
        return user.approval_status == UserApprovalStatus.APPROVED
    return False


def require_contact_access(user: User = Depends(get_current_user)) -> User:
    if not can_view_contact(user):
        raise ForbiddenError(
            "Your recruiter account must be approved before you can contact students."
        )
    return user


def require_roles(*roles: UserRole):
    def _checker(user: User = Depends(get_current_user)) -> User:
        if user.role not in roles:
            raise ForbiddenError("Insufficient role.")
        return user

    return _checker


require_super_admin = require_roles(UserRole.SUPER_ADMIN)
# The legacy school-admin path is retired — RankAfrica is now fully
# student-driven, so these resolve to super-admin-only. Endpoints that used to
# accept a SCHOOL_ADMIN are now super-admin curation tools; a SCHOOL_ADMIN role
# has no write access anywhere.
require_school_admin = require_super_admin
require_university_admin = require_super_admin
require_evaluator = require_roles(UserRole.SUPER_ADMIN, UserRole.EVALUATOR)


def get_current_student(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Student:
    """Resolve the Student profile linked to a self-registered STUDENT account."""
    if user.role != UserRole.STUDENT:
        raise ForbiddenError("This action is only available to student accounts.")
    student = db.query(Student).filter(Student.user_id == user.id).first()
    if not student:
        raise NotFoundError("No student profile is linked to this account.")
    return student


def require_permission(key: str):
    """Gate an endpoint on a fine-grained permission (see app.core.permissions)."""

    def _checker(user: User = Depends(get_current_user)) -> User:
        if not has_permission(user, key):
            raise ForbiddenError("You don't have permission to do that.")
        return user

    return _checker


def assert_university_scope(actor: User, university_id: str) -> None:
    """A SCHOOL_ADMIN may only touch their own university's resources.

    SUPER_ADMINs bypass this check entirely.
    """
    if actor.role == UserRole.SUPER_ADMIN:
        return
    # Company staff with the upload permission act across all registered
    # schools, so they are not bound to a single university.
    if actor.role == UserRole.EMPLOYEE and has_permission(actor, UPLOAD_TRANSCRIPTS):
        return
    if actor.role in SCHOOL_ADMIN_ROLES:
        if not actor.university_id or actor.university_id != university_id:
            raise ForbiddenError("You can only manage students from your own school.")
        return
    raise ForbiddenError("Insufficient role.")


def assert_school_approved(actor: User, university: University | None) -> None:
    """Block write actions for school admins whose school isn't yet approved.

    SUPER_ADMINs bypass entirely. If the school is PENDING or REJECTED we
    surface a clear message so the frontend can show it verbatim.
    """
    if actor.role == UserRole.SUPER_ADMIN:
        return
    # Company staff upload only for already-registered (approved) schools.
    if actor.role == UserRole.EMPLOYEE:
        if university is None or university.approval_status != SchoolApprovalStatus.APPROVED:
            raise ForbiddenError("Transcripts can only be uploaded for an approved school.")
        return
    if actor.role not in SCHOOL_ADMIN_ROLES:
        return  # other roles are governed by their own RBAC checks
    if university is None:
        raise ForbiddenError("Your account is not linked to a school yet.")
    status = university.approval_status
    if status == SchoolApprovalStatus.APPROVED:
        return
    if status == SchoolApprovalStatus.PENDING:
        raise ForbiddenError(
            f"{university.name} is still pending review. You can view your "
            "dashboard but cannot upload student data until a RankAfrica "
            "Super Admin approves your school."
        )
    if status == SchoolApprovalStatus.REJECTED:
        raise ForbiddenError(
            f"{university.name}'s registration was rejected"
            + (f": {university.approval_notes}" if university.approval_notes else ".")
            + " Please contact info@rankafrica.org."
        )
    raise ForbiddenError("School approval status unknown.")
