"""Student approval queue — Super Admin gates which submissions go public."""
from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session, joinedload

from app.api.deps import get_current_user, require_super_admin
from app.core.exceptions import NotFoundError
from app.db.session import get_db
from app.models.student import ApprovalStatus, Student
from app.models.submission_cycle import CycleStatus
from app.models.user import User
from app.schemas.student import StudentApprovalIn, StudentOut
from app.services import audit_service

router = APIRouter()


@router.get(
    "/pending",
    response_model=list[StudentOut],
    dependencies=[Depends(require_super_admin)],
)
def list_pending(
    db: Session = Depends(get_db),
    cycle_id: str | None = None,
    limit: int = Query(100, ge=1, le=500),
) -> list[StudentOut]:
    q = (
        db.query(Student)
        .options(joinedload(Student.university), joinedload(Student.field))
        .filter(Student.approval_status == ApprovalStatus.PENDING)
    )
    if cycle_id:
        q = q.filter(Student.submission_cycle_id == cycle_id)
    rows = q.order_by(Student.created_at.desc()).limit(limit).all()
    return [StudentOut.model_validate(r) for r in rows]


@router.post(
    "/{student_id}",
    response_model=StudentOut,
    dependencies=[Depends(require_super_admin)],
)
def set_approval(
    student_id: str,
    payload: StudentApprovalIn,
    db: Session = Depends(get_db),
    actor: User = Depends(get_current_user),
) -> StudentOut:
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise NotFoundError("Student not found.")

    student.approval_status = payload.approval_status
    student.approval_notes = payload.approval_notes
    student.approved_by_id = actor.id
    student.approved_at = (
        datetime.now(timezone.utc)
        if payload.approval_status == ApprovalStatus.APPROVED
        else None
    )

    # Visibility rule: an approved student is only PUBLIC if their cycle has
    # been PUBLISHED. Spec: "Approved leaderboard becomes publicly visible
    # until the cycle closes."
    if payload.approval_status == ApprovalStatus.APPROVED and student.submission_cycle:
        if student.submission_cycle.status in (CycleStatus.PUBLISHED, CycleStatus.CLOSED):
            student.is_publicly_visible = True
    else:
        student.is_publicly_visible = False

    audit_service.record(
        db,
        actor=actor,
        action="student.approval",
        entity_type="student",
        entity_id=student.id,
        metadata={"status": payload.approval_status.value},
    )
    db.commit()
    db.refresh(student)
    return StudentOut.model_validate(student)
