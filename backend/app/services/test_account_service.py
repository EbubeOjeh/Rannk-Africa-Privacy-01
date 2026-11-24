"""CEO/admin dummy test accounts.

The CEO/admin creates throwaway logins (student / recruiter / school-admin) from
the dashboard to exercise every flow. Each is flagged ``is_test_account`` and is
**auto-deleted 20 days after creation** — the admin can also block or delete one
manually before then. Deletion removes the linked Student (and, via ON DELETE
CASCADE, all of that student's profile data) so nothing is left behind.
"""
from __future__ import annotations

import math
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, NotFoundError, ValidationError
from app.core.security import hash_password
from app.models.field import Field
from app.models.student import ApprovalStatus, Student
from app.models.university import University
from app.models.user import User, UserApprovalStatus, UserRole
from app.schemas.test_account import TestAccountCreate, TestAccountOut
from app.services.field_mapping import map_course_to_field

# Dummy accounts live for 20 days, then are purged from the database.
TEST_ACCOUNT_TTL_DAYS = 20

_ROLE_TO_TYPE = {
    UserRole.STUDENT: "student",
    UserRole.EMPLOYER: "recruiter",
    UserRole.SCHOOL_ADMIN: "school_admin",
    UserRole.UNIVERSITY_ADMIN: "school_admin",
}


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _as_aware(dt: datetime) -> datetime:
    """created_at may come back naive (SQLite); treat it as UTC for the math."""
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


def _expires_at(user: User) -> datetime:
    return _as_aware(user.created_at) + timedelta(days=TEST_ACCOUNT_TTL_DAYS)


def is_expired(user: User) -> bool:
    return user.is_test_account and _expires_at(user) <= _now()


def _to_out(db: Session, user: User) -> TestAccountOut:
    exp = _expires_at(user)
    days_left = max(0, math.ceil((exp - _now()).total_seconds() / 86400))
    uni_name = None
    if user.university_id:
        uni = db.query(University).filter(University.id == user.university_id).first()
        uni_name = uni.name if uni else None
    return TestAccountOut(
        id=user.id,
        account_type=_ROLE_TO_TYPE.get(user.role, user.role.value),
        name=user.name,
        email=user.email,
        role=user.role.value,
        is_active=user.is_active,
        approval_status=user.approval_status.value if user.approval_status else None,
        organization=user.organization,
        university_name=uni_name,
        created_at=user.created_at,
        expires_at=exp,
        days_left=days_left,
    )


def _default_university(db: Session) -> University | None:
    return db.query(University).order_by(University.created_at.asc()).first()


def create_test_account(db: Session, payload: TestAccountCreate) -> TestAccountOut:
    email = payload.email.lower()
    if db.query(User).filter(User.email == email).first():
        raise ConflictError("An account with this email already exists.")

    password_hash = hash_password(payload.password)
    common = dict(
        name=payload.name.strip(),
        email=email,
        password_hash=password_hash,
        is_active=True,
        is_email_verified=True,
        is_test_account=True,
    )

    if payload.account_type == "student":
        university = None
        if payload.university_id:
            university = db.query(University).filter(University.id == payload.university_id).first()
            if not university:
                raise ValidationError("Unknown university.")
        university = university or _default_university(db)
        if not university:
            raise ValidationError("Create a university first, then add a test student.")

        user = User(role=UserRole.STUDENT, approval_status=UserApprovalStatus.APPROVED, **common)
        db.add(user)
        db.flush()

        field = None
        if payload.course:
            slug = map_course_to_field(payload.course)
            field = db.query(Field).filter(Field.slug == slug).first()

        student = Student(
            full_name=payload.name.strip(),
            email=email,
            university_id=university.id,
            field_id=field.id if field else None,
            course=(payload.course or None),
            is_self_registered=True,
            user_id=user.id,
            terms_accepted_at=_now(),
            approval_status=ApprovalStatus.PENDING,
            is_publicly_visible=False,
        )
        db.add(student)

    elif payload.account_type == "recruiter":
        user = User(
            role=UserRole.EMPLOYER,
            approval_status=UserApprovalStatus.PENDING,
            organization=(payload.organization or payload.name).strip(),
            **common,
        )
        db.add(user)

    elif payload.account_type == "school_admin":
        if not payload.university_id:
            raise ValidationError("Pick a university for the test school admin.")
        university = db.query(University).filter(University.id == payload.university_id).first()
        if not university:
            raise ValidationError("Unknown university.")
        user = User(role=UserRole.SCHOOL_ADMIN, university_id=university.id, **common)
        db.add(user)

    else:  # pragma: no cover - guarded by the schema Literal
        raise ValidationError("Unknown account type.")

    db.commit()
    db.refresh(user)
    return _to_out(db, user)


def list_test_accounts(db: Session) -> list[TestAccountOut]:
    """List every dummy account (after opportunistically purging expired ones)."""
    purge_expired(db)
    rows = (
        db.query(User)
        .filter(User.is_test_account.is_(True))
        .order_by(User.created_at.desc())
        .all()
    )
    return [_to_out(db, u) for u in rows]


def _load_test_user(db: Session, user_id: str) -> User:
    user = db.query(User).filter(User.id == user_id, User.is_test_account.is_(True)).first()
    if not user:
        raise NotFoundError("Test account not found.")
    return user


def set_blocked(db: Session, user_id: str, blocked: bool) -> TestAccountOut:
    user = _load_test_user(db, user_id)
    user.is_active = not blocked
    db.commit()
    db.refresh(user)
    return _to_out(db, user)


def _delete_user_and_profile(db: Session, user: User) -> None:
    """Delete a test user plus its linked Student (whose children cascade)."""
    student = db.query(Student).filter(Student.user_id == user.id).first()
    if student:
        db.delete(student)
    db.delete(user)


def delete_test_account(db: Session, user_id: str) -> None:
    user = _load_test_user(db, user_id)
    _delete_user_and_profile(db, user)
    db.commit()


def purge_expired(db: Session) -> int:
    """Delete every test account past its 20-day TTL. Returns the count removed."""
    cutoff = _now() - timedelta(days=TEST_ACCOUNT_TTL_DAYS)
    expired = (
        db.query(User)
        .filter(User.is_test_account.is_(True), User.created_at < cutoff)
        .all()
    )
    for user in expired:
        _delete_user_and_profile(db, user)
    if expired:
        db.commit()
    return len(expired)
