"""AI integrity flags — admin review queue (PRS §7, §13).

Super-admins list integrity flags raised by the AI verification suite, trigger
a fresh scan of a student, and confirm/dismiss flags. Confirmed flags are then
acted on by the ranking/approval flows; everything here is review tooling.
"""
from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_super_admin
from app.core.exceptions import NotFoundError
from app.db.session import get_db
from app.models.ai_flag import FLAG_LABELS, AIFlag, FlagStatus, FlagType
from app.models.student import Student
from app.models.user import User
from app.schemas.flag import FlagOut, FlagResolve
from app.services import ai_integrity, audit_service

router = APIRouter()


def _to_out(flag: AIFlag, student: Student | None = None) -> FlagOut:
    """Serialise a flag, filling student_name + label manually."""
    out = FlagOut.model_validate(flag)
    out.label = FLAG_LABELS.get(flag.flag_type)
    if student is not None:
        out.student_name = student.full_name
    elif flag.student is not None:
        out.student_name = flag.student.full_name
    return out


@router.get("", response_model=list[FlagOut], dependencies=[Depends(require_super_admin)])
def list_flags(
    status: FlagStatus | None = Query(default=None),
    flag_type: FlagType | None = Query(default=None),
    student_id: str | None = Query(default=None),
    db: Session = Depends(get_db),
) -> list[FlagOut]:
    """List integrity flags. Defaults to OPEN flags when no status is given."""
    q = db.query(AIFlag, Student).outerjoin(Student, AIFlag.student_id == Student.id)
    q = q.filter(AIFlag.status == (status if status is not None else FlagStatus.OPEN))
    if flag_type is not None:
        q = q.filter(AIFlag.flag_type == flag_type)
    if student_id is not None:
        q = q.filter(AIFlag.student_id == student_id)
    rows = q.order_by(AIFlag.created_at.desc()).limit(200).all()
    return [_to_out(flag, student) for flag, student in rows]


@router.post(
    "/scan/{student_id}",
    response_model=list[FlagOut],
    dependencies=[Depends(require_super_admin)],
)
def scan_student(
    student_id: str,
    db: Session = Depends(get_db),
    actor: User = Depends(get_current_user),
) -> list[FlagOut]:
    """Run the integrity suite over a student and return their OPEN flags."""
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise NotFoundError("Student not found.")

    flags = ai_integrity.scan_student(db, student)
    audit_service.record(
        db,
        actor=actor,
        action="flags.scan",
        entity_type="student",
        entity_id=student.id,
        metadata={"open_flags": len(flags)},
    )
    db.commit()
    open_flags = [f for f in flags if f.status == FlagStatus.OPEN]
    return [_to_out(flag, student) for flag in open_flags]


@router.post(
    "/{flag_id}/resolve",
    response_model=FlagOut,
    dependencies=[Depends(require_super_admin)],
)
def resolve_flag(
    flag_id: str,
    payload: FlagResolve,
    db: Session = Depends(get_db),
    actor: User = Depends(get_current_user),
) -> FlagOut:
    """Confirm or dismiss a flag after manual review."""
    flag = db.query(AIFlag).filter(AIFlag.id == flag_id).first()
    if not flag:
        raise NotFoundError("Flag not found.")

    flag.status = payload.status
    flag.review_notes = payload.review_notes
    flag.reviewed_by_id = actor.id
    flag.reviewed_at = datetime.now(timezone.utc)

    audit_service.record(
        db,
        actor=actor,
        action="flags.resolve",
        entity_type="ai_flag",
        entity_id=flag.id,
        metadata={"status": payload.status.value},
    )
    db.commit()
    db.refresh(flag)
    return _to_out(flag)


@router.get("/stats", dependencies=[Depends(require_super_admin)])
def flag_stats(db: Session = Depends(get_db)) -> dict[str, int]:
    """Counts of flags by review status for the dashboard."""
    counts = {"open": 0, "confirmed": 0, "dismissed": 0}
    rows = (
        db.query(AIFlag.status, func.count(AIFlag.id))
        .group_by(AIFlag.status)
        .all()
    )
    for flag_status, n in rows:
        counts[flag_status.value] = n
    return counts
