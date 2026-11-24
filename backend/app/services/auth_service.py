"""Auth service — signup, login, token issuance, school self-registration."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, NotFoundError, UnauthorizedError, ValidationError
from app.core.security import (
    _create_token,
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.core.terms import TERMS_CONFIRMATION
from app.models.field import Field
from app.models.notification import Notification
from app.models.student import ApprovalStatus, Student
from app.models.terms_acceptance import CURRENT_TERMS_VERSION, TermsAcceptance
from app.models.university import SchoolApprovalStatus, University
from app.models.user import User, UserApprovalStatus, UserRole
from app.schemas.auth import (
    AuthResponse,
    AuthUser,
    LoginRequest,
    PasswordResetConfirm,
    RecruiterRegisterRequest,
    SignupRequest,
    StudentRegisterRequest,
    TokenPair,
)
from app.services.field_mapping import map_course_to_field
from app.utils.slug import slugify
from app.validators.email_domain import (
    extract_apex_domain,
    is_free_email,
    looks_institutional,
)


def signup(db: Session, payload: SignupRequest) -> AuthResponse:
    existing = db.query(User).filter(User.email == payload.email.lower()).first()
    if existing:
        raise ConflictError("An account with this email already exists.")

    if payload.university_id:
        uni = db.query(University).filter(University.id == payload.university_id).first()
        if not uni:
            raise ValidationError("Unknown university_id.")

    # Self-serve signup is constrained to safe roles only. Students use
    # /register-student and staff are provisioned by a super admin; school
    # self-registration has been retired (the platform is fully student-driven),
    # so a generic signup lands as EMPLOYER. SUPER_ADMIN / EVALUATOR cannot be
    # self-assigned.
    requested = payload.role
    if requested == UserRole.SUPER_ADMIN or requested == UserRole.EVALUATOR:
        raise ValidationError("This role cannot be self-assigned.")
    role = UserRole.EMPLOYER

    user = User(
        name=payload.name.strip(),
        email=payload.email.lower(),
        password_hash=hash_password(payload.password),
        role=role,
        university_id=payload.university_id,
        organization=(payload.organization or None),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return _build_auth_response(user)


def register_recruiter(
    db: Session,
    payload: RecruiterRegisterRequest,
    *,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> AuthResponse:
    """Public — a recruiter/employer self-registers and enters the approval
    queue. They can sign in immediately but only see public student data until
    an admin approves them. They must accept the Terms & Conditions (PRS §18)."""
    if not payload.accept_terms:
        raise ValidationError("You must accept the Terms & Conditions to register.")

    email = payload.email.lower()
    if db.query(User).filter(User.email == email).first():
        raise ConflictError("An account with this email already exists.")

    user = User(
        name=payload.name.strip(),
        email=email,
        password_hash=hash_password(payload.password),
        role=UserRole.EMPLOYER,
        organization=payload.organization.strip(),
        approval_status=UserApprovalStatus.PENDING,
        is_active=True,
        is_email_verified=False,
    )
    db.add(user)
    db.flush()

    # Record the Terms acceptance for legal cover (no linked Student — user only).
    db.add(
        TermsAcceptance(
            user_id=user.id,
            student_id=None,
            version=CURRENT_TERMS_VERSION,
            ip_address=ip_address,
            user_agent=user_agent,
            accepted_text=TERMS_CONFIRMATION,
        )
    )

    # Notify every admin/CEO so the request shows up in their queue.
    admins = db.query(User).filter(User.role == UserRole.SUPER_ADMIN).all()
    for admin in admins:
        db.add(
            Notification(
                user_id=admin.id,
                title="New recruiter awaiting approval",
                body=f"{user.name} ({user.organization or 'no org'}) requested recruiter access.",
                link="/admin/recruiters",
                category="approval",
            )
        )

    # Also send an email to the admins (best-effort; a no-op unless SMTP is
    # configured, and never fatal to the registration itself).
    from app.services import notification_service  # local import avoids a cycle

    org = user.organization or "an organization"
    notification_service.email_admins(
        db,
        subject="New recruiter / organization registration — RankAfrica",
        body=(
            f"A new recruiter/organization has registered and is awaiting approval.\n\n"
            f"  Name:         {user.name}\n"
            f"  Organization: {org}\n"
            f"  Email:        {user.email}\n\n"
            f"Review and approve them in the admin dashboard under Recruiters "
            f"(/admin/recruiters)."
        ),
    )

    db.commit()
    db.refresh(user)
    return _build_auth_response(user)


def register_student(
    db: Session,
    payload: StudentRegisterRequest,
    *,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> AuthResponse:
    """PRS §4 — a student self-registers. Creates a STUDENT user + a linked
    Student profile (pending verification), auto-maps course→field, and records
    the Terms & Conditions acceptance (PRS §18). The student can sign in
    immediately and build their profile; an admin/school verifies before they
    become publicly visible (hybrid model)."""
    if not payload.accept_terms:
        raise ValidationError("You must accept the Terms & Conditions to register.")

    email = payload.email.lower()
    if db.query(User).filter(User.email == email).first():
        raise ConflictError("An account with this email already exists.")

    university = _resolve_student_university(db, payload)

    # Course → one of the 8 canonical fields.
    field_slug = map_course_to_field(payload.course)
    field = db.query(Field).filter(Field.slug == field_slug).first()

    user = User(
        name=payload.name.strip(),
        email=email,
        password_hash=hash_password(payload.password),
        role=UserRole.STUDENT,
        approval_status=UserApprovalStatus.APPROVED,  # students sign in immediately
        is_active=True,
        is_email_verified=False,
    )
    db.add(user)
    db.flush()

    from app.services import cycle_service  # local import avoids any cycle

    active = cycle_service.get_active_cycle(db)
    now = datetime.now(timezone.utc)

    student = Student(
        full_name=payload.name.strip(),
        email=email,
        phone_number=payload.phone_number,
        gender=payload.gender,
        university_id=university.id,
        field_id=field.id if field else None,
        course=payload.course.strip(),
        faculty=(payload.faculty or None),
        academic_level=payload.academic_level,
        year_of_study=payload.year_of_study,
        submission_cycle_id=active.id if active else None,
        is_self_registered=True,
        user_id=user.id,
        terms_accepted_at=now,
        approval_status=ApprovalStatus.PENDING,
        is_publicly_visible=False,
    )
    db.add(student)
    db.flush()

    db.add(
        TermsAcceptance(
            user_id=user.id,
            student_id=student.id,
            version=CURRENT_TERMS_VERSION,
            ip_address=ip_address,
            user_agent=user_agent,
            accepted_text=TERMS_CONFIRMATION,
        )
    )

    for admin in db.query(User).filter(User.role == UserRole.SUPER_ADMIN).all():
        db.add(
            Notification(
                user_id=admin.id,
                title="New student profile awaiting verification",
                body=f"{student.full_name} ({university.name}) self-registered.",
                link="/admin/approvals",
                category="approval",
            )
        )

    db.commit()
    db.refresh(user)
    return _build_auth_response(user)


def _resolve_student_university(db: Session, payload: StudentRegisterRequest) -> University:
    """Pick an existing university by id/name, or create a PENDING one so a
    student from any school can register (hybrid model)."""
    if payload.university_id:
        uni = db.query(University).filter(University.id == payload.university_id).first()
        if not uni:
            raise ValidationError("Unknown university_id.")
        return uni
    name = (payload.university_name or "").strip()
    if not name:
        raise ValidationError("Select your university or enter its name.")
    existing = db.query(University).filter(University.name.ilike(name)).first()
    if existing:
        return existing
    uni = University(
        name=name,
        slug=slugify(name),
        country="Nigeria",
        state=payload.state,
        institution_type="university",
        grading_system="5_point",
        tier=3,
        approval_status=SchoolApprovalStatus.PENDING,
    )
    db.add(uni)
    db.flush()
    return uni


def login(db: Session, payload: LoginRequest) -> AuthResponse:
    user = db.query(User).filter(User.email == payload.email.lower()).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise UnauthorizedError("Invalid email or password.")
    # A dummy test account past its 20-day TTL is treated as already deleted —
    # purge it now and reject the login.
    if user.is_test_account:
        from app.services import test_account_service  # local import avoids a cycle

        if test_account_service.is_expired(user):
            test_account_service.delete_test_account(db, user.id)
            raise UnauthorizedError("Invalid email or password.")
    if not user.is_active:
        raise UnauthorizedError("Account is deactivated.")
    return _build_auth_response(user)


def refresh(db: Session, refresh_token: str) -> TokenPair:
    payload = decode_token(refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise UnauthorizedError("Invalid refresh token.")
    user = db.query(User).filter(User.id == payload["sub"]).first()
    if not user or not user.is_active:
        raise UnauthorizedError("Account unavailable.")
    return TokenPair(
        access_token=create_access_token(user.id, role=user.role.value),
        refresh_token=create_refresh_token(user.id),
    )


def request_password_reset(db: Session, email: str) -> str | None:
    """Issue a short-lived reset token. Returns the token (in real life it would be emailed)."""
    user = db.query(User).filter(User.email == email.lower()).first()
    if not user:
        return None
    return _create_token(user.id, timedelta(minutes=30), "password_reset")


def confirm_password_reset(db: Session, payload: PasswordResetConfirm) -> None:
    decoded = decode_token(payload.token)
    if not decoded or decoded.get("type") != "password_reset":
        raise UnauthorizedError("Invalid or expired reset token.")
    user = db.query(User).filter(User.id == decoded["sub"]).first()
    if not user:
        raise NotFoundError("Account not found.")
    user.password_hash = hash_password(payload.new_password)
    db.commit()


def issue_email_verification_token(user: User) -> str:
    return _create_token(user.id, timedelta(hours=24), "email_verify")


def confirm_email_verification(db: Session, token: str) -> User:
    decoded = decode_token(token)
    if not decoded or decoded.get("type") != "email_verify":
        raise UnauthorizedError("Invalid or expired verification token.")
    user = db.query(User).filter(User.id == decoded["sub"]).first()
    if not user:
        raise NotFoundError("Account not found.")
    user.is_email_verified = True
    db.commit()
    return user


def _build_auth_response(user: User, *, school: University | None = None) -> AuthResponse:
    if school is None and user.university_id:
        school = user.university
    auth_user = _hydrate_auth_user(user, school)
    return AuthResponse(
        user=auth_user,
        tokens=TokenPair(
            access_token=create_access_token(user.id, role=user.role.value),
            refresh_token=create_refresh_token(user.id),
        ),
    )


def _hydrate_auth_user(user: User, school: University | None) -> AuthUser:
    from app.core.permissions import get_permissions

    data = AuthUser.model_validate(user).model_dump()
    data["permissions"] = sorted(get_permissions(user))
    data["approval_status"] = user.approval_status.value if user.approval_status else None
    company_role = getattr(user, "company_role", None)
    data["company_role_name"] = company_role.name if company_role else None
    if school is not None:
        data["school_approval_status"] = school.approval_status.value
        data["school_name"] = school.name
    return AuthUser.model_validate(data)


def change_password(db: Session, user: User, current_password: str, new_password: str) -> None:
    if not verify_password(current_password, user.password_hash):
        raise UnauthorizedError("Current password is incorrect.")
    user.password_hash = hash_password(new_password)
    user.must_change_password = False
    db.commit()
