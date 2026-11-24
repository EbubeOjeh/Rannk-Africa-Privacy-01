"""Auth endpoints."""
from fastapi import APIRouter, Depends, Request, status, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.terms import terms_info
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import (
    AuthResponse,
    AuthUser,
    ChangePasswordRequest,
    LoginRequest,
    PasswordResetConfirm,
    PasswordResetRequest,
    RecruiterRegisterRequest,
    RefreshRequest,
    SignupRequest,
    StudentRegisterRequest,
    TermsInfo,
    TokenPair,
)
from app.schemas.common import MessageResponse
from app.services import auth_service

router = APIRouter()


@router.get("/terms", response_model=TermsInfo)
def get_terms() -> TermsInfo:
    """PRS §18 — the Terms & Conditions text + version shown before submission."""
    return TermsInfo(**terms_info())


@router.post("/signup", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def signup(payload: SignupRequest, db: Session = Depends(get_db)) -> AuthResponse:
    raise HTTPException(410, 'Use /student-register for open classroom accounts.')


@router.post(
    "/register-recruiter",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_recruiter(
    payload: RecruiterRegisterRequest,
    request: Request,
    db: Session = Depends(get_db),
) -> AuthResponse:
    """Public — a recruiter/employer self-registers, accepts the Terms (PRS §18),
    and enters the approval queue."""
    return auth_service.register_recruiter(
        db,
        payload,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )


@router.post(
    "/register-student",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_student(
    payload: StudentRegisterRequest,
    request: Request,
    db: Session = Depends(get_db),
) -> AuthResponse:
    """Public (PRS §4) — a student self-registers, accepts the Terms (PRS §18),
    and gets a profile auto-assigned to one of the eight fields by their course."""
    raise HTTPException(410, 'Use the classroom registration page at /student-register; it assigns synthetic academic data.')
    return auth_service.register_student(
        db,
        payload,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )


@router.post("/login", response_model=AuthResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> AuthResponse:
    return auth_service.login(db, payload)


@router.post("/refresh", response_model=TokenPair)
def refresh(payload: RefreshRequest, db: Session = Depends(get_db)) -> TokenPair:
    return auth_service.refresh(db, payload.refresh_token)


@router.get("/me", response_model=AuthUser)
def me(user: User = Depends(get_current_user)) -> AuthUser:
    return auth_service._hydrate_auth_user(user, user.university)


@router.post("/change-password", response_model=MessageResponse)
def change_password(
    payload: ChangePasswordRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> MessageResponse:
    auth_service.change_password(db, user, payload.current_password, payload.new_password)
    return MessageResponse(message="Password updated.")


@router.post("/password-reset/request", response_model=MessageResponse)
def password_reset_request(
    payload: PasswordResetRequest, db: Session = Depends(get_db)
) -> MessageResponse:
    token = auth_service.request_password_reset(db, payload.email)
    return MessageResponse(
        message="If that email exists, a reset link has been sent."
        + (f" (dev token: {token})" if token else "")
    )


@router.post("/password-reset/confirm", response_model=MessageResponse)
def password_reset_confirm(
    payload: PasswordResetConfirm, db: Session = Depends(get_db)
) -> MessageResponse:
    auth_service.confirm_password_reset(db, payload)
    return MessageResponse(message="Password updated.")


@router.post("/email/request-verification", response_model=MessageResponse)
def request_email_verification(user: User = Depends(get_current_user)) -> MessageResponse:
    token = auth_service.issue_email_verification_token(user)
    return MessageResponse(message=f"Verification token issued (dev): {token}")


@router.post("/email/verify", response_model=AuthUser)
def verify_email(token: str, db: Session = Depends(get_db)) -> AuthUser:
    user = auth_service.confirm_email_verification(db, token)
    return auth_service._hydrate_auth_user(user, user.university)
