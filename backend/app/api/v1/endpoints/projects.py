"""Project submission endpoints — final-year project + AI rubric scoring."""
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
from app.core.exceptions import NotFoundError, ValidationError
from app.db.session import get_db
from app.models.project_submission import ProjectStatus, ProjectSubmission
from app.models.student import Student
from app.models.user import User
from app.schemas.common import MessageResponse
from app.schemas.project import (
    ProjectModerationIn,
    ProjectSubmissionIn,
    ProjectSubmissionOut,
)
from app.services import audit_service, file_storage
from app.services.evaluation_engine import evaluate_student, score_project
from app.validators.files import ALLOWED_DOC, ALLOWED_PDF, ALLOWED_VIDEO, validate_upload

router = APIRouter()


def _load_student(db: Session, student_id: str) -> Student:
    s = db.query(Student).filter(Student.id == student_id).first()
    if not s:
        raise NotFoundError("Student not found.")
    return s


@router.get("/by-student/{student_id}", response_model=ProjectSubmissionOut | None)
def get_project_for_student(
    student_id: str, db: Session = Depends(get_db)
) -> ProjectSubmissionOut | None:
    project = (
        db.query(ProjectSubmission)
        .filter(ProjectSubmission.student_id == student_id)
        .first()
    )
    return ProjectSubmissionOut.model_validate(project) if project else None


@router.post(
    "/by-student/{student_id}",
    response_model=ProjectSubmissionOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_school_admin)],
)
def upsert_project(
    student_id: str,
    payload: ProjectSubmissionIn,
    db: Session = Depends(get_db),
    actor: User = Depends(get_current_user),
) -> ProjectSubmissionOut:
    student = _load_student(db, student_id)
    assert_university_scope(actor, student.university_id)
    assert_school_approved(actor, student.university)

    project = (
        db.query(ProjectSubmission)
        .filter(ProjectSubmission.student_id == student.id)
        .first()
    )
    if project is None:
        project = ProjectSubmission(student_id=student.id, **payload.model_dump())
        db.add(project)
    else:
        for k, v in payload.model_dump(exclude_unset=True).items():
            setattr(project, k, v)
        project.status = ProjectStatus.PENDING  # re-evaluation required after edits
        project.originality = project.technical_depth = 0.0
        project.problem_solving = project.innovation = 0.0
        project.total_score = 0.0
        project.evaluated_at = None
    db.commit()
    db.refresh(project)

    audit_service.record(
        db,
        actor=actor,
        action="project.upsert",
        entity_type="project_submission",
        entity_id=project.id,
    )
    db.commit()
    return ProjectSubmissionOut.model_validate(project)


@router.post(
    "/by-student/{student_id}/files",
    response_model=ProjectSubmissionOut,
    dependencies=[Depends(require_school_admin)],
)
async def upload_project_files(
    student_id: str,
    report: UploadFile | None = File(default=None),
    demo_video: UploadFile | None = File(default=None),
    source_code_url: str | None = Form(default=None),
    db: Session = Depends(get_db),
    actor: User = Depends(get_current_user),
) -> ProjectSubmissionOut:
    student = _load_student(db, student_id)
    assert_university_scope(actor, student.university_id)
    assert_school_approved(actor, student.university)

    project = (
        db.query(ProjectSubmission)
        .filter(ProjectSubmission.student_id == student.id)
        .first()
    )
    if project is None:
        raise NotFoundError("Submit project metadata before uploading files.")

    if report:
        validate_upload(report, allowed=ALLOWED_PDF)
        project.report_url = file_storage.save_upload(report, subdir=f"projects/{student.id}")
    if demo_video:
        validate_upload(demo_video, allowed=ALLOWED_VIDEO | {".pdf"})  # accept image previews too
        project.demo_video_url = file_storage.save_upload(
            demo_video, subdir=f"projects/{student.id}"
        )
    if source_code_url:
        project.source_code_url = source_code_url.strip()
    db.commit()
    db.refresh(project)
    return ProjectSubmissionOut.model_validate(project)


@router.post(
    "/by-student/{student_id}/evaluate",
    response_model=ProjectSubmissionOut,
    dependencies=[Depends(require_school_admin)],
)
def evaluate_project(
    student_id: str,
    db: Session = Depends(get_db),
    actor: User = Depends(get_current_user),
) -> ProjectSubmissionOut:
    """Run the Claude rubric scorer against the student's project submission."""
    student = _load_student(db, student_id)
    assert_university_scope(actor, student.university_id)
    assert_school_approved(actor, student.university)

    project = (
        db.query(ProjectSubmission)
        .filter(ProjectSubmission.student_id == student.id)
        .first()
    )
    if not project:
        raise NotFoundError("No project submission for this student.")

    outcome = score_project(project, field_slug=(student.field.slug if student.field else None))
    project.originality = outcome.originality
    project.technical_depth = outcome.technical_depth
    project.problem_solving = outcome.problem_solving
    project.innovation = outcome.innovation
    project.total_score = outcome.score
    project.ai_engine = outcome.engine
    project.ai_reasoning = outcome.reasoning
    project.evaluated_at = datetime.now(timezone.utc) if outcome.status == "evaluated" else None
    project.status = {
        "evaluated": ProjectStatus.EVALUATED,
        "pending": ProjectStatus.PENDING,
        "failed": ProjectStatus.FAILED,
    }.get(outcome.status, ProjectStatus.PENDING)

    db.flush()
    # Refresh the student's composite score now that project_score has changed.
    db.refresh(student)
    evaluate_student(db, student)

    audit_service.record(
        db,
        actor=actor,
        action="project.evaluate",
        entity_type="project_submission",
        entity_id=project.id,
        metadata={
            "engine": outcome.engine,
            "status": outcome.status,
            "score": outcome.score,
            "error": outcome.error,
        },
    )
    db.commit()
    db.refresh(project)
    return ProjectSubmissionOut.model_validate(project)


@router.post(
    "/by-student/{student_id}/moderate",
    response_model=ProjectSubmissionOut,
    dependencies=[Depends(require_super_admin)],
)
def moderate_project(
    student_id: str,
    payload: ProjectModerationIn,
    db: Session = Depends(get_db),
    actor: User = Depends(get_current_user),
) -> ProjectSubmissionOut:
    """Human moderation layer — Super Admin overrides AI rubric scores."""
    student = _load_student(db, student_id)
    project = (
        db.query(ProjectSubmission)
        .filter(ProjectSubmission.student_id == student.id)
        .first()
    )
    if not project:
        raise NotFoundError("No project submission for this student.")

    project.originality = payload.originality
    project.technical_depth = payload.technical_depth
    project.problem_solving = payload.problem_solving
    project.innovation = payload.innovation
    project.total_score = round(
        payload.originality + payload.technical_depth + payload.problem_solving + payload.innovation,
        2,
    )
    project.moderator_notes = payload.moderator_notes
    project.moderated_at = datetime.now(timezone.utc)
    project.status = ProjectStatus.MODERATED

    db.flush()
    db.refresh(student)
    evaluate_student(db, student)

    audit_service.record(
        db,
        actor=actor,
        action="project.moderate",
        entity_type="project_submission",
        entity_id=project.id,
    )
    db.commit()
    db.refresh(project)
    return ProjectSubmissionOut.model_validate(project)


@router.delete(
    "/by-student/{student_id}",
    response_model=MessageResponse,
    dependencies=[Depends(require_school_admin)],
)
def delete_project(
    student_id: str,
    db: Session = Depends(get_db),
    actor: User = Depends(get_current_user),
) -> MessageResponse:
    student = _load_student(db, student_id)
    assert_university_scope(actor, student.university_id)
    assert_school_approved(actor, student.university)
    project = (
        db.query(ProjectSubmission)
        .filter(ProjectSubmission.student_id == student.id)
        .first()
    )
    if not project:
        raise NotFoundError("No project submission for this student.")
    db.delete(project)
    db.commit()
    return MessageResponse(message="Project submission deleted.")
