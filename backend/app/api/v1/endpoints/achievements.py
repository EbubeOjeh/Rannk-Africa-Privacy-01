"""Achievement endpoints — submit, list, verify."""
from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, File, Form, UploadFile, status
from sqlalchemy.orm import Session

from app.api.deps import (
    assert_school_approved,
    assert_university_scope,
    get_current_user,
    require_school_admin,
    require_super_admin,
)
from app.core.exceptions import NotFoundError
from app.db.session import get_db
from app.models.achievement import (
    ACHIEVEMENT_CAP,
    ACHIEVEMENT_LABELS,
    ACHIEVEMENT_POINTS,
    Achievement,
    AchievementType,
    VerificationStatus,
)
from app.models.student import Student
from app.models.user import User
from app.schemas.achievement import (
    AchievementCatalog,
    AchievementCatalogItem,
    AchievementIn,
    AchievementOut,
    AchievementVerify,
)
from app.schemas.common import MessageResponse
from app.services import audit_service, file_storage
from app.services.evaluation_engine import evaluate_student
from app.validators.files import ALLOWED_DOC, validate_upload

router = APIRouter()


@router.get("/catalog", response_model=AchievementCatalog)
def achievement_catalog() -> AchievementCatalog:
    """Static reference: the six achievement types, their labels, and points."""
    return AchievementCatalog(
        items=[
            AchievementCatalogItem(
                type=t,
                label=ACHIEVEMENT_LABELS[t],
                points=ACHIEVEMENT_POINTS[t],
            )
            for t in AchievementType
        ],
        cap=ACHIEVEMENT_CAP,
    )


@router.get("/by-student/{student_id}", response_model=list[AchievementOut])
def list_for_student(student_id: str, db: Session = Depends(get_db)) -> list[AchievementOut]:
    rows = (
        db.query(Achievement)
        .filter(Achievement.student_id == student_id)
        .order_by(Achievement.created_at.desc())
        .all()
    )
    return [AchievementOut.model_validate(r) for r in rows]


@router.post(
    "/by-student/{student_id}",
    response_model=AchievementOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_school_admin)],
)
async def submit_achievement(
    student_id: str,
    type: AchievementType = Form(...),
    title: str = Form(...),
    description: str | None = Form(default=None),
    link: str | None = Form(default=None),
    evidence: UploadFile | None = File(default=None),
    db: Session = Depends(get_db),
    actor: User = Depends(get_current_user),
) -> AchievementOut:
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise NotFoundError("Student not found.")
    assert_university_scope(actor, student.university_id)
    assert_school_approved(actor, student.university)

    evidence_url = None
    if evidence:
        validate_upload(evidence, allowed=ALLOWED_DOC)
        evidence_url = file_storage.save_upload(evidence, subdir=f"achievements/{student.id}")

    achievement = Achievement(
        student_id=student.id,
        type=type,
        points=ACHIEVEMENT_POINTS[type],
        title=title.strip(),
        description=(description or "").strip() or None,
        link=(link or "").strip() or None,
        evidence_url=evidence_url,
        verification_status=VerificationStatus.UNVERIFIED,
    )
    db.add(achievement)
    db.flush()

    audit_service.record(
        db,
        actor=actor,
        action="achievement.submit",
        entity_type="achievement",
        entity_id=achievement.id,
    )
    db.commit()
    db.refresh(achievement)
    return AchievementOut.model_validate(achievement)


@router.post(
    "/{achievement_id}/verify",
    response_model=AchievementOut,
    dependencies=[Depends(require_super_admin)],
)
def verify_achievement(
    achievement_id: str,
    payload: AchievementVerify,
    db: Session = Depends(get_db),
    actor: User = Depends(get_current_user),
) -> AchievementOut:
    a = db.query(Achievement).filter(Achievement.id == achievement_id).first()
    if not a:
        raise NotFoundError("Achievement not found.")
    a.verification_status = payload.verification_status
    a.rejection_reason = payload.rejection_reason
    a.verified_by_id = actor.id
    a.verified_at = (
        datetime.now(timezone.utc)
        if payload.verification_status == VerificationStatus.VERIFIED
        else None
    )

    db.flush()
    student = db.query(Student).filter(Student.id == a.student_id).first()
    if student:
        evaluate_student(db, student)

    audit_service.record(
        db,
        actor=actor,
        action="achievement.verify",
        entity_type="achievement",
        entity_id=a.id,
        metadata={"status": payload.verification_status.value},
    )
    db.commit()
    db.refresh(a)
    return AchievementOut.model_validate(a)


@router.delete(
    "/{achievement_id}",
    response_model=MessageResponse,
    dependencies=[Depends(require_school_admin)],
)
def delete_achievement(
    achievement_id: str,
    db: Session = Depends(get_db),
    actor: User = Depends(get_current_user),
) -> MessageResponse:
    a = db.query(Achievement).filter(Achievement.id == achievement_id).first()
    if not a:
        raise NotFoundError("Achievement not found.")
    student = db.query(Student).filter(Student.id == a.student_id).first()
    if student:
        assert_university_scope(actor, student.university_id)
    db.delete(a)
    db.flush()
    if student:
        evaluate_student(db, student)
    db.commit()
    return MessageResponse(message="Achievement deleted.")
