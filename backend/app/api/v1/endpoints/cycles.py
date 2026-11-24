"""Submission cycle endpoints — Super Admin owns the lifecycle."""
from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import require_super_admin
from app.core.exceptions import ConflictError, NotFoundError
from app.db.session import get_db
from app.models.submission_cycle import CycleStatus, SubmissionCycle
from app.schemas.common import MessageResponse
from app.schemas.cycle import CycleCreate, CycleOut, CycleStatusUpdate, CycleUpdate
from app.services import cycle_service

router = APIRouter()


@router.get("", response_model=list[CycleOut])
def list_cycles(db: Session = Depends(get_db)) -> list[CycleOut]:
    rows = db.query(SubmissionCycle).order_by(SubmissionCycle.year.desc(), SubmissionCycle.created_at.desc()).all()
    return [CycleOut.model_validate(r) for r in rows]


@router.get("/active", response_model=CycleOut | None)
def get_active_cycle(db: Session = Depends(get_db)) -> CycleOut | None:
    """The cycle currently accepting submissions (or in review)."""
    cycle = cycle_service.get_active_cycle(db)
    return CycleOut.model_validate(cycle) if cycle else None


@router.get("/published", response_model=CycleOut | None)
def get_published_cycle(db: Session = Depends(get_db)) -> CycleOut | None:
    """The cycle whose leaderboard is publicly visible right now."""
    cycle = cycle_service.get_published_cycle(db)
    return CycleOut.model_validate(cycle) if cycle else None


@router.get("/{cycle_id}", response_model=CycleOut)
def get_cycle(cycle_id: str, db: Session = Depends(get_db)) -> CycleOut:
    c = db.query(SubmissionCycle).filter(SubmissionCycle.id == cycle_id).first()
    if not c:
        raise NotFoundError("Cycle not found.")
    return CycleOut.model_validate(c)


@router.post(
    "",
    response_model=CycleOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_super_admin)],
)
def create_cycle(payload: CycleCreate, db: Session = Depends(get_db)) -> CycleOut:
    if db.query(SubmissionCycle).filter(SubmissionCycle.name == payload.name).first():
        raise ConflictError("A cycle with that name already exists.")
    cycle = SubmissionCycle(**payload.model_dump())
    db.add(cycle)
    db.commit()
    db.refresh(cycle)
    return CycleOut.model_validate(cycle)


@router.patch(
    "/{cycle_id}",
    response_model=CycleOut,
    dependencies=[Depends(require_super_admin)],
)
def update_cycle(cycle_id: str, payload: CycleUpdate, db: Session = Depends(get_db)) -> CycleOut:
    cycle = db.query(SubmissionCycle).filter(SubmissionCycle.id == cycle_id).first()
    if not cycle:
        raise NotFoundError("Cycle not found.")
    if cycle.is_locked:
        raise ConflictError("Cycle is locked; cannot edit.")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(cycle, k, v)
    db.commit()
    db.refresh(cycle)
    return CycleOut.model_validate(cycle)


@router.post(
    "/{cycle_id}/status",
    response_model=CycleOut,
    dependencies=[Depends(require_super_admin)],
)
def change_cycle_status(
    cycle_id: str, payload: CycleStatusUpdate, db: Session = Depends(get_db)
) -> CycleOut:
    cycle = db.query(SubmissionCycle).filter(SubmissionCycle.id == cycle_id).first()
    if not cycle:
        raise NotFoundError("Cycle not found.")
    cycle_service.transition(db, cycle, payload.status)
    db.commit()
    db.refresh(cycle)
    return CycleOut.model_validate(cycle)


@router.delete(
    "/{cycle_id}",
    response_model=MessageResponse,
    dependencies=[Depends(require_super_admin)],
)
def delete_cycle(cycle_id: str, db: Session = Depends(get_db)) -> MessageResponse:
    cycle = db.query(SubmissionCycle).filter(SubmissionCycle.id == cycle_id).first()
    if not cycle:
        raise NotFoundError("Cycle not found.")
    if cycle.status != CycleStatus.DRAFT:
        raise ConflictError("Only DRAFT cycles can be deleted.")
    db.delete(cycle)
    db.commit()
    return MessageResponse(message="Cycle deleted.")
