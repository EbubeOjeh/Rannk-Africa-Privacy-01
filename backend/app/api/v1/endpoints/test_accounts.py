"""Dummy test accounts (PRS testing aid).

The CEO/admin creates throwaway logins to exercise the student / recruiter /
school flows. Accounts auto-delete 20 days after creation; they can also be
blocked or deleted manually here. Gated on the ``manage_team`` permission, held
by the technical admin (SUPER_ADMIN) and the CEO (``full_access``).
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import require_permission
from app.core.permissions import MANAGE_TEAM
from app.db.session import get_db
from app.schemas.common import MessageResponse
from app.schemas.test_account import TestAccountCreate, TestAccountOut
from app.services import test_account_service

router = APIRouter(dependencies=[Depends(require_permission(MANAGE_TEAM))])


@router.get("", response_model=list[TestAccountOut])
def list_accounts(db: Session = Depends(get_db)) -> list[TestAccountOut]:
    return test_account_service.list_test_accounts(db)


@router.post("", response_model=TestAccountOut, status_code=status.HTTP_201_CREATED)
def create_account(payload: TestAccountCreate, db: Session = Depends(get_db)) -> TestAccountOut:
    return test_account_service.create_test_account(db, payload)


@router.post("/{user_id}/block", response_model=TestAccountOut)
def block_account(user_id: str, db: Session = Depends(get_db)) -> TestAccountOut:
    return test_account_service.set_blocked(db, user_id, True)


@router.post("/{user_id}/unblock", response_model=TestAccountOut)
def unblock_account(user_id: str, db: Session = Depends(get_db)) -> TestAccountOut:
    return test_account_service.set_blocked(db, user_id, False)


@router.delete("/{user_id}", response_model=MessageResponse)
def delete_account(user_id: str, db: Session = Depends(get_db)) -> MessageResponse:
    test_account_service.delete_test_account(db, user_id)
    return MessageResponse(message="Test account deleted.")


@router.post("/purge", response_model=MessageResponse)
def purge_accounts(db: Session = Depends(get_db)) -> MessageResponse:
    removed = test_account_service.purge_expired(db)
    return MessageResponse(message=f"Removed {removed} expired test account(s).")
