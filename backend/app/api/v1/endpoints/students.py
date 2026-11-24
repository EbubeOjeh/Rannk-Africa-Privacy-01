"""Student endpoints."""
from __future__ import annotations

from fastapi import APIRouter, Depends, File, Form, Query, UploadFile, status
from sqlalchemy.orm import Session, joinedload

from app.api.deps import (
    assert_school_approved,
    assert_university_scope,
    can_view_contact,
    get_current_user,
    get_current_user_optional,
    require_school_admin,
)
from app.models.university import University
from app.core.exceptions import NotFoundError
from app.db.session import get_db
from app.models.student import ApprovalStatus, Student
from app.models.submission_cycle import CycleStatus
from app.models.user import User, UserRole
from app.schemas.common import MessageResponse, Page, PageMeta
from app.schemas.me import StudentMeOut
from app.schemas.student import StudentCreate, StudentOut, StudentUpdate
from app.services import audit_service, cycle_service, file_storage, student_profile
from app.services.evaluation_engine import evaluate_student
from app.validators.files import ALLOWED_IMAGE, validate_upload

router = APIRouter()


@router.get("", response_model=Page[StudentOut])
def list_students(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    q: str | None = None,
    university_id: str | None = None,
    field_id: str | None = None,
    department_id: str | None = None,
    approval_status: ApprovalStatus | None = None,
    cycle_id: str | None = None,
):
    query = db.query(Student).options(
        joinedload(Student.university), joinedload(Student.field), joinedload(Student.department)
    )
    if q:
        query = query.filter(Student.full_name.ilike(f"%{q}%"))
    if university_id:
        query = query.filter(Student.university_id == university_id)
    if field_id:
        query = query.filter(Student.field_id == field_id)
    if department_id:
        query = query.filter(Student.department_id == department_id)
    if approval_status:
        query = query.filter(Student.approval_status == approval_status)
    if cycle_id:
        query = query.filter(Student.submission_cycle_id == cycle_id)

    total = query.count()
    rows = (
        query.order_by(Student.overall_rank.asc().nullslast(), Student.final_score.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return Page[StudentOut](
        items=[StudentOut.model_validate(r) for r in rows],
        meta=PageMeta(
            page=page,
            page_size=page_size,
            total=total,
            total_pages=max(1, (total + page_size - 1) // page_size),
        ),
    )


@router.get("/{student_id}", response_model=StudentOut)
def get_student(
    student_id: str,
    db: Session = Depends(get_db),
    viewer: User | None = Depends(get_current_user_optional),
) -> StudentOut:
    s = db.query(Student).filter(Student.id == student_id).first()
    staff = can_view_contact(viewer)
    is_owner = bool(viewer and viewer.role == UserRole.STUDENT and s and s.user_id == viewer.id)
    # Don't leak a student who isn't publicly visible via a guessed/known id —
    # only staff, approved recruiters, or the student themselves may see them.
    if not s or (not s.is_publicly_visible and not staff and not is_owner):
        raise NotFoundError("Student not found.")
    out = StudentOut.model_validate(s)
    # Private contact details are only exposed to internal staff and approved
    # recruiters. Everyone else sees the public profile (name, school, scores).
    if not staff:
        out.email = None
        out.phone_number = None
        out.linkedin_url = None
    return out


@router.get("/{student_id}/full", response_model=StudentMeOut)
def get_student_full(
    student_id: str,
    db: Session = Depends(get_db),
    viewer: User | None = Depends(get_current_user_optional),
) -> StudentMeOut:
    """Public rich profile (PRS §9) — photo, bio, scores, ranks, badges, projects,
    research, experience, competitions, achievements + professional links.

    Hidden unless the student is publicly visible (staff/approved employers may
    preview). Direct contact channels are gated to approved viewers."""
    s = db.query(Student).filter(Student.id == student_id).first()
    staff = can_view_contact(viewer)
    is_owner = bool(viewer and viewer.role == UserRole.STUDENT and s and s.user_id == viewer.id)
    if not s or (not s.is_publicly_visible and not staff and not is_owner):
        raise NotFoundError("Student not found.")
    return student_profile.build_student_out(db, s, include_contact=staff or is_owner)


@router.post(
    "",
    response_model=StudentOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_school_admin)],
)
def create_student(
    payload: StudentCreate,
    db: Session = Depends(get_db),
    actor: User = Depends(get_current_user),
) -> StudentOut:
    assert_university_scope(actor, payload.university_id)
    school = db.query(University).filter(University.id == payload.university_id).first()
    assert_school_approved(actor, school)

    # If a cycle is supplied (or one is active), enforce the 15-per-school cap.
    cycle_id = payload.submission_cycle_id
    if cycle_id is None:
        active = cycle_service.get_active_cycle(db)
        cycle_id = active.id if active and active.status == CycleStatus.OPEN else None
    if cycle_id:
        cycle_service.assert_can_submit(db, cycle_id=cycle_id, university_id=payload.university_id)

    data = payload.model_dump()
    data["submission_cycle_id"] = cycle_id
    s = Student(**data)
    db.add(s)
    db.flush()

    # Run the WES-style academic evaluation immediately so the new student
    # has a score the moment they're created (project/achievements are 0
    # until those pipelines are filled in separately).
    if s.raw_cgpa is not None or s.raw_gpa is not None:
        db.refresh(s)
        evaluate_student(db, s)

    audit_service.record(
        db,
        actor=actor,
        action="student.create",
        entity_type="student",
        entity_id=s.id,
    )
    db.commit()
    db.refresh(s)
    return StudentOut.model_validate(s)


@router.patch(
    "/{student_id}",
    response_model=StudentOut,
    dependencies=[Depends(require_school_admin)],
)
def update_student(
    student_id: str,
    payload: StudentUpdate,
    db: Session = Depends(get_db),
    actor: User = Depends(get_current_user),
) -> StudentOut:
    s = db.query(Student).filter(Student.id == student_id).first()
    if not s:
        raise NotFoundError("Student not found.")
    assert_university_scope(actor, s.university_id)
    assert_school_approved(actor, s.university)

    if s.submission_cycle and s.submission_cycle.is_locked:
        from app.core.exceptions import ConflictError
        raise ConflictError("Student belongs to a locked cycle; cannot edit.")

    fields = payload.model_dump(exclude_unset=True)
    for k, v in fields.items():
        setattr(s, k, v)
    # Re-evaluate if any score-relevant field changed.
    if fields.keys() & {"raw_gpa", "raw_cgpa", "gpa_scale", "credits_earned"}:
        evaluate_student(db, s)
    db.commit()
    db.refresh(s)
    return StudentOut.model_validate(s)


@router.post(
    "/{student_id}/avatar",
    response_model=StudentOut,
    dependencies=[Depends(require_school_admin)],
)
async def upload_avatar(
    student_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    actor: User = Depends(get_current_user),
) -> StudentOut:
    s = db.query(Student).filter(Student.id == student_id).first()
    if not s:
        raise NotFoundError("Student not found.")
    assert_university_scope(actor, s.university_id)
    assert_school_approved(actor, s.university)

    validate_upload(file, allowed=ALLOWED_IMAGE)
    s.avatar_url = file_storage.save_upload(file, subdir=f"avatars/{s.id}")
    db.commit()
    db.refresh(s)
    return StudentOut.model_validate(s)


@router.delete(
    "/{student_id}",
    response_model=MessageResponse,
    dependencies=[Depends(require_school_admin)],
)
def delete_student(
    student_id: str,
    db: Session = Depends(get_db),
    actor: User = Depends(get_current_user),
) -> MessageResponse:
    s = db.query(Student).filter(Student.id == student_id).first()
    if not s:
        raise NotFoundError("Student not found.")
    assert_university_scope(actor, s.university_id)

    db.delete(s)
    db.commit()
    return MessageResponse(message="Student deleted.")
