"""Recruiter / employer approval queue (PDF: Recruiter Verification & Access).

Recruiters self-register via /auth/register-recruiter and land here PENDING.
Staff with the ``approve_recruiters`` permission approve or reject them; only
APPROVED recruiters can see student contact details or message students.
"""
from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from app.api.deps import require_permission
from app.core.exceptions import NotFoundError
from app.core.permissions import APPROVE_RECRUITERS
from app.db.session import get_db
from app.models.user import User, UserApprovalStatus, UserRole
from app.schemas.common import MessageResponse

router = APIRouter()


class RecruiterOut(BaseModel):
    id: str
    name: str
    email: EmailStr
    organization: str | None = None
    approval_status: str
    is_active: bool = True
    created_at: datetime | None = None

    model_config = {"from_attributes": True}


def _out(u: User) -> RecruiterOut:
    data = RecruiterOut.model_validate(u).model_dump()
    data["approval_status"] = u.approval_status.value if u.approval_status else "approved"
    return RecruiterOut.model_validate(data)


@router.get("", response_model=list[RecruiterOut], dependencies=[Depends(require_permission(APPROVE_RECRUITERS))])
def list_recruiters(
    db: Session = Depends(get_db),
    status: UserApprovalStatus | None = Query(default=None),
) -> list[RecruiterOut]:
    q = db.query(User).filter(User.role == UserRole.EMPLOYER)
    if status:
        q = q.filter(User.approval_status == status)
    return [_out(u) for u in q.order_by(User.created_at.desc()).all()]


@router.get("/pending", response_model=list[RecruiterOut], dependencies=[Depends(require_permission(APPROVE_RECRUITERS))])
def list_pending(db: Session = Depends(get_db)) -> list[RecruiterOut]:
    rows = (
        db.query(User)
        .filter(User.role == UserRole.EMPLOYER, User.approval_status == UserApprovalStatus.PENDING)
        .order_by(User.created_at.desc())
        .all()
    )
    return [_out(u) for u in rows]


def _get_recruiter(db: Session, recruiter_id: str) -> User:
    u = db.query(User).filter(User.id == recruiter_id, User.role == UserRole.EMPLOYER).first()
    if not u:
        raise NotFoundError("Recruiter not found.")
    return u


@router.post("/{recruiter_id}/approve", response_model=RecruiterOut, dependencies=[Depends(require_permission(APPROVE_RECRUITERS))])
def approve(recruiter_id: str, db: Session = Depends(get_db)) -> RecruiterOut:
    u = _get_recruiter(db, recruiter_id)
    u.approval_status = UserApprovalStatus.APPROVED
    u.is_active = True
    db.commit()
    db.refresh(u)
    return _out(u)


@router.post("/{recruiter_id}/reject", response_model=RecruiterOut, dependencies=[Depends(require_permission(APPROVE_RECRUITERS))])
def reject(recruiter_id: str, db: Session = Depends(get_db)) -> RecruiterOut:
    u = _get_recruiter(db, recruiter_id)
    u.approval_status = UserApprovalStatus.REJECTED
    db.commit()
    db.refresh(u)
    return _out(u)
