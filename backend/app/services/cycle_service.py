"""SubmissionCycle service — state transitions, 15-student cap, locking."""
from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, NotFoundError, ValidationError
from app.models.student import ApprovalStatus, Student
from app.models.submission_cycle import CycleStatus, SubmissionCycle


def get_active_cycle(db: Session) -> SubmissionCycle | None:
    """Return the cycle that's currently OPEN or in REVIEW, if any."""
    return (
        db.query(SubmissionCycle)
        .filter(SubmissionCycle.status.in_([CycleStatus.OPEN, CycleStatus.REVIEW]))
        .order_by(SubmissionCycle.year.desc())
        .first()
    )


def get_published_cycle(db: Session) -> SubmissionCycle | None:
    """Return the most recent PUBLISHED cycle (whose approved students are public)."""
    return (
        db.query(SubmissionCycle)
        .filter(SubmissionCycle.status == CycleStatus.PUBLISHED)
        .order_by(SubmissionCycle.year.desc(), SubmissionCycle.published_at.desc().nullslast())
        .first()
    )


def assert_can_submit(db: Session, *, cycle_id: str | None, university_id: str) -> SubmissionCycle:
    """Validate that a school may submit a new student right now.

    - Cycle must exist and be in OPEN status.
    - Cycle must not be locked.
    - The school must not have already submitted ``max_students_per_school`` students in this cycle.
    """
    cycle = _require_cycle(db, cycle_id)
    if cycle.status != CycleStatus.OPEN:
        raise ConflictError(
            f"Cycle '{cycle.name}' is not open for submissions (status={cycle.status.value})."
        )
    if cycle.is_locked:
        raise ConflictError(f"Cycle '{cycle.name}' is locked.")

    submitted = (
        db.query(func.count(Student.id))
        .filter(Student.submission_cycle_id == cycle.id)
        .filter(Student.university_id == university_id)
        .scalar()
        or 0
    )
    if submitted >= cycle.max_students_per_school:
        raise ConflictError(
            f"School quota reached: {submitted}/{cycle.max_students_per_school} "
            f"students already submitted for cycle '{cycle.name}'."
        )
    return cycle


def transition(db: Session, cycle: SubmissionCycle, new_status: CycleStatus) -> SubmissionCycle:
    """Move a cycle through its lifecycle, enforcing legal transitions."""
    valid_transitions: dict[CycleStatus, set[CycleStatus]] = {
        CycleStatus.DRAFT:     {CycleStatus.OPEN},
        CycleStatus.OPEN:      {CycleStatus.REVIEW, CycleStatus.PUBLISHED},
        CycleStatus.REVIEW:    {CycleStatus.PUBLISHED, CycleStatus.OPEN},
        CycleStatus.PUBLISHED: {CycleStatus.CLOSED},
        CycleStatus.CLOSED:    set(),
    }
    if new_status not in valid_transitions.get(cycle.status, set()):
        raise ValidationError(
            f"Illegal cycle transition: {cycle.status.value} -> {new_status.value}"
        )

    now = datetime.now(timezone.utc)
    cycle.status = new_status
    if new_status == CycleStatus.PUBLISHED:
        cycle.published_at = now
        # Make all APPROVED students in this cycle publicly visible.
        db.query(Student).filter(
            Student.submission_cycle_id == cycle.id,
            Student.approval_status == ApprovalStatus.APPROVED,
        ).update({"is_publicly_visible": True}, synchronize_session=False)
    elif new_status == CycleStatus.CLOSED:
        cycle.closed_at = now
        cycle.is_locked = True
    return cycle


def _require_cycle(db: Session, cycle_id: str | None) -> SubmissionCycle:
    if not cycle_id:
        raise ValidationError("submission_cycle_id is required.")
    cycle = db.query(SubmissionCycle).filter(SubmissionCycle.id == cycle_id).first()
    if not cycle:
        raise NotFoundError(f"SubmissionCycle '{cycle_id}' not found.")
    return cycle
