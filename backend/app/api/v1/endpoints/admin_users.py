"""Admin user moderation (PRS §13 — suspend/unsuspend accounts).

Suspending sets ``is_active = False`` so the user can no longer authenticate
(``get_current_user`` rejects inactive accounts); the reason/timestamp are
retained for the audit trail. Super Admins cannot be suspended.
"""
from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_super_admin
from app.core.exceptions import NotFoundError, ValidationError
from app.db.session import get_db
from app.models.user import User, UserRole
from app.schemas.common import MessageResponse
from app.services import audit_service

router = APIRouter()


class SuspendIn(BaseModel):
    reason: str | None = None


@router.post(
    "/{user_id}/suspend",
    response_model=MessageResponse,
    dependencies=[Depends(require_super_admin)],
)
def suspend_user(
    user_id: str,
    payload: SuspendIn,
    db: Session = Depends(get_db),
    actor: User = Depends(get_current_user),
) -> MessageResponse:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise NotFoundError("User not found.")
    if user.role == UserRole.SUPER_ADMIN:
        raise ValidationError("Super Admin accounts cannot be suspended.")

    user.is_active = False
    user.suspension_reason = payload.reason
    user.suspended_at = datetime.now(timezone.utc)

    audit_service.record(
        db,
        actor=actor,
        action="user.suspend",
        entity_type="user",
        entity_id=user.id,
        metadata={"reason": payload.reason},
    )
    db.commit()
    return MessageResponse(message="User suspended.")


@router.post(
    "/{user_id}/unsuspend",
    response_model=MessageResponse,
    dependencies=[Depends(require_super_admin)],
)
def unsuspend_user(
    user_id: str,
    db: Session = Depends(get_db),
    actor: User = Depends(get_current_user),
) -> MessageResponse:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise NotFoundError("User not found.")

    user.is_active = True
    user.suspension_reason = None
    user.suspended_at = None

    audit_service.record(
        db,
        actor=actor,
        action="user.unsuspend",
        entity_type="user",
        entity_id=user.id,
    )
    db.commit()
    return MessageResponse(message="User reinstated.")


@router.get("/suspended", dependencies=[Depends(require_super_admin)])
def list_suspended(db: Session = Depends(get_db)) -> list[dict]:
    users = (
        db.query(User)
        .filter(User.is_active.is_(False))
        .order_by(User.suspended_at.desc())
        .all()
    )
    return [
        {
            "id": u.id,
            "name": u.name,
            "email": u.email,
            "role": u.role.value,
            "suspension_reason": u.suspension_reason,
            "suspended_at": u.suspended_at,
        }
        for u in users
    ]
