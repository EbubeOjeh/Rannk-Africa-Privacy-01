"""Student self-service surface (PRS §5, §9, §11) — mounted at /me.

A self-registered STUDENT manages their own profile, projects, research,
experience, competitions, leadership, achievements and CV, and sees their
dashboard. Every write re-evaluates the student's /100 score and re-syncs
verification badges.
"""
from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, File, Form, UploadFile, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_student
from app.core.exceptions import ForbiddenError, NotFoundError
from app.db.session import get_db
from app.models.achievement import (
    ACHIEVEMENT_POINTS,
    Achievement,
    AchievementType,
    VerificationStatus,
)
from app.models.badge import BADGE_EMOJI, BADGE_LABELS
from app.models.competition import Competition
from app.models.experience import Experience
from app.models.field import Field
from app.models.leadership import LeadershipActivity
from app.models.project_submission import ProjectStatus, ProjectSubmission
from app.models.research import ResearchPublication
from app.models.student import Student
from app.schemas.achievement import AchievementOut
from app.schemas.common import MessageResponse
from app.schemas.competition import CompetitionIn, CompetitionOut
from app.schemas.experience import ExperienceIn, ExperienceOut
from app.schemas.leadership import LeadershipIn, LeadershipOut
from app.schemas.me import BadgeOut, DashboardOut, StudentMeOut, StudentMeUpdate
from app.schemas.project import ProjectSubmissionIn, ProjectSubmissionOut
from app.schemas.research import ResearchIn, ResearchOut
from app.services import badge_service, file_storage, scoring_config, student_dashboard
from app.services.evaluation_engine import (
    evaluate_student,
    score_profile,
    score_project,
    uses_project_model,
)
from app.services.field_mapping import map_course_to_field
from app.validators.files import ALLOWED_DOC, ALLOWED_IMAGE, ALLOWED_PDF, validate_upload

router = APIRouter()


# --------------------------------------------------------------------------- #
#  Helpers
# --------------------------------------------------------------------------- #
def _recompute(db: Session, student: Student) -> None:
    """Re-evaluate the score and re-sync badges after any profile change."""
    evaluate_student(db, student)
    badge_service.sync_badges(db, student)


def _score_profile_statement(db: Session, student: Student) -> None:
    """AI-score the free-text "Achievements & Profile Assessment" out of /60.

    No-op for Technology/Music (they use the project model). Callers recompute
    the /100 afterwards so the new /60 flows into the final score.
    """
    if uses_project_model(student.field.slug if student.field else None):
        return
    outcome = score_profile(student)
    student.profile_score = outcome.score
    db.flush()


def _me_out(db: Session, student: Student) -> StudentMeOut:
    weights = scoring_config.get_weights(db)
    badges = [
        BadgeOut(
            badge_key=b.badge_key,
            label=BADGE_LABELS.get(b.badge_key, b.badge_key),
            emoji=BADGE_EMOJI.get(b.badge_key, "🏅"),
            is_auto=b.is_auto,
        )
        for b in (student.badges or [])
    ]
    return StudentMeOut(
        id=student.id,
        user_id=student.user_id,
        full_name=student.full_name,
        email=student.email,
        avatar_url=student.avatar_url,
        resume_url=student.resume_url,
        transcript_url=student.transcript_url,
        bio=student.bio,
        profile_statement=student.profile_statement,
        profile_score=student.profile_score,
        gender=student.gender,
        university_id=student.university_id,
        university_name=student.university.name if student.university else None,
        faculty=student.faculty,
        department_id=student.department_id,
        course=student.course,
        field_id=student.field_id,
        field_name=student.field.name if student.field else None,
        field_slug=student.field.slug if student.field else None,
        academic_level=student.academic_level,
        year_of_study=student.year_of_study,
        phone_number=student.phone_number,
        whatsapp_number=student.whatsapp_number,
        linkedin_url=student.linkedin_url,
        github_url=student.github_url,
        behance_url=student.behance_url,
        portfolio_url=student.portfolio_url,
        google_scholar_url=student.google_scholar_url,
        music_url=student.music_url,
        skills=student.skills or [],
        languages=student.languages or [],
        raw_cgpa=student.raw_cgpa,
        gpa_scale=student.gpa_scale,
        normalized_cgpa=student.normalized_cgpa,
        standardized_gpa_4=student.standardized_gpa_4,
        class_of_degree=student.class_of_degree,
        credits_earned=student.credits_earned,
        scores=student_dashboard.score_components(student, weights),
        approval_status=student.approval_status,
        is_publicly_visible=student.is_publicly_visible,
        is_self_registered=student.is_self_registered,
        terms_accepted_at=student.terms_accepted_at,
        overall_rank=student.overall_rank,
        field_rank=student.field_rank,
        university_rank=student.university_rank,
        badges=badges,
        projects=[ProjectSubmissionOut.model_validate(p) for p in (student.projects or [])],
        research=[ResearchOut.model_validate(r) for r in (student.research_items or [])],
        experiences=[ExperienceOut.model_validate(e) for e in (student.experiences or [])],
        competitions=[CompetitionOut.model_validate(c) for c in (student.competitions or [])],
        leadership=[LeadershipOut.model_validate(le) for le in (student.leadership_items or [])],
        achievements=[AchievementOut.model_validate(a) for a in (student.achievements or [])],
    )


def _owned(item, student: Student):
    if item is None or item.student_id != student.id:
        raise NotFoundError("Item not found.")
    return item


# --------------------------------------------------------------------------- #
#  Profile + dashboard
# --------------------------------------------------------------------------- #
@router.get("", response_model=StudentMeOut)
def get_me(db: Session = Depends(get_db), student: Student = Depends(get_current_student)) -> StudentMeOut:
    return _me_out(db, student)


@router.get("/dashboard", response_model=DashboardOut)
def my_dashboard(db: Session = Depends(get_db), student: Student = Depends(get_current_student)) -> DashboardOut:
    return student_dashboard.build_dashboard(db, student)


@router.patch("", response_model=StudentMeOut)
def update_me(
    payload: StudentMeUpdate,
    db: Session = Depends(get_db),
    student: Student = Depends(get_current_student),
) -> StudentMeOut:
    fields = payload.model_dump(exclude_unset=True)
    from app.models.classroom import ClassroomEnrollment
    from app.services.classroom import ACADEMIC_FIELDS
    from fastapi import HTTPException
    if db.get(ClassroomEnrollment, student.user_id) and fields.keys() & ACADEMIC_FIELDS:
        # Existing Details form can submit unchanged values. Reject only edits.
        changed = [k for k in fields.keys() & ACADEMIC_FIELDS if (None if fields[k] == '' else fields[k]) != getattr(student,k,None)]
        if changed:
            raise HTTPException(400, 'Assigned fictional academic values are read-only so they match your synthetic transcript. Use Privacy and Study tasks for the evaluation.')
    for key, value in fields.items():
        setattr(student, key, value)

    # Course change re-maps the field automatically (PRS §4).
    if "course" in fields and student.course:
        slug = map_course_to_field(student.course)
        field = db.query(Field).filter(Field.slug == slug).first()
        if field:
            student.field_id = field.id

    db.flush()
    db.refresh(student)
    # Saving the Profile Assessment text (re-)scores it out of /60 for
    # profile-model fields, so the /100 reflects it immediately.
    if "profile_statement" in fields:
        _score_profile_statement(db, student)
    _recompute(db, student)
    db.commit()
    db.refresh(student)
    return _me_out(db, student)


@router.post("/evaluate-profile", response_model=StudentMeOut)
def evaluate_my_profile(
    db: Session = Depends(get_db),
    student: Student = Depends(get_current_student),
) -> StudentMeOut:
    """Re-run the AI "Achievements & Profile Assessment" (/60) for the current
    student's profile statement (profile-model fields only), then recompute."""
    _score_profile_statement(db, student)
    db.refresh(student)
    _recompute(db, student)
    db.commit()
    db.refresh(student)
    return _me_out(db, student)


@router.post("/avatar", response_model=StudentMeOut)
async def upload_my_avatar(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    student: Student = Depends(get_current_student),
) -> StudentMeOut:
    # An upload stores the owner's chosen photo; discovery still requires the
    # independently saved audience and photo choices in the privacy policy.
    validate_upload(file, allowed=ALLOWED_IMAGE)
    student.avatar_url = file_storage.save_upload(file, subdir=f"avatars/{student.id}")
    db.commit()
    db.refresh(student)
    return _me_out(db, student)


@router.post("/resume", response_model=StudentMeOut)
async def upload_my_resume(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    student: Student = Depends(get_current_student),
) -> StudentMeOut:
    from app.models.classroom import ClassroomEnrollment
    from fastapi import HTTPException
    if db.get(ClassroomEnrollment, student.user_id):
        raise HTTPException(400, 'Classroom profiles use assigned synthetic records. CV and transcript uploads remain disabled.')
    validate_upload(file, allowed=ALLOWED_PDF | ALLOWED_DOC)
    student.resume_url = file_storage.save_upload(file, subdir=f"resumes/{student.id}")
    db.commit()
    db.refresh(student)
    return _me_out(db, student)


@router.post("/transcript", response_model=StudentMeOut)
async def upload_my_transcript(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    student: Student = Depends(get_current_student),
) -> StudentMeOut:
    """Upload an UNOFFICIAL transcript / semester results (final-year students
    rarely have an official transcript yet). PDF, document or image."""
    from app.models.classroom import ClassroomEnrollment
    from fastapi import HTTPException
    if db.get(ClassroomEnrollment, student.user_id):
        raise HTTPException(400, 'Classroom profiles use assigned synthetic records. CV and transcript uploads remain disabled.')
    validate_upload(file, allowed=ALLOWED_PDF | ALLOWED_DOC | ALLOWED_IMAGE)
    student.transcript_url = file_storage.save_upload(file, subdir=f"transcripts/{student.id}")
    db.commit()
    db.refresh(student)
    return _me_out(db, student)


# --------------------------------------------------------------------------- #
#  Projects (PRS §5 — students may upload several)
# --------------------------------------------------------------------------- #
@router.get("/projects", response_model=list[ProjectSubmissionOut])
def my_projects(student: Student = Depends(get_current_student)) -> list[ProjectSubmissionOut]:
    return [ProjectSubmissionOut.model_validate(p) for p in (student.projects or [])]


@router.post("/projects", response_model=ProjectSubmissionOut, status_code=status.HTTP_201_CREATED)
def add_my_project(
    payload: ProjectSubmissionIn,
    db: Session = Depends(get_db),
    student: Student = Depends(get_current_student),
) -> ProjectSubmissionOut:
    project = ProjectSubmission(student_id=student.id, status=ProjectStatus.PENDING, **payload.model_dump())
    db.add(project)
    db.flush()
    db.refresh(student)
    _recompute(db, student)
    db.commit()
    db.refresh(project)
    return ProjectSubmissionOut.model_validate(project)


@router.post("/projects/{project_id}/evaluate", response_model=ProjectSubmissionOut)
def evaluate_my_project(
    project_id: str,
    db: Session = Depends(get_db),
    student: Student = Depends(get_current_student),
) -> ProjectSubmissionOut:
    project = _owned(db.query(ProjectSubmission).filter(ProjectSubmission.id == project_id).first(), student)
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
    db.refresh(student)
    _recompute(db, student)
    db.commit()
    db.refresh(project)
    return ProjectSubmissionOut.model_validate(project)


@router.post("/projects/{project_id}/files", response_model=ProjectSubmissionOut)
async def upload_my_project_files(
    project_id: str,
    report: UploadFile | None = File(default=None),
    source_code_url: str | None = Form(default=None),
    demo_video_url: str | None = Form(default=None),
    db: Session = Depends(get_db),
    student: Student = Depends(get_current_student),
) -> ProjectSubmissionOut:
    project = _owned(db.query(ProjectSubmission).filter(ProjectSubmission.id == project_id).first(), student)
    if report:
        validate_upload(report, allowed=ALLOWED_PDF)
        project.report_url = file_storage.save_upload(report, subdir=f"projects/{student.id}")
    if source_code_url:
        project.source_code_url = source_code_url.strip()
    if demo_video_url:
        project.demo_video_url = demo_video_url.strip()
    db.commit()
    db.refresh(project)
    return ProjectSubmissionOut.model_validate(project)


@router.delete("/projects/{project_id}", response_model=MessageResponse)
def delete_my_project(
    project_id: str,
    db: Session = Depends(get_db),
    student: Student = Depends(get_current_student),
) -> MessageResponse:
    project = _owned(db.query(ProjectSubmission).filter(ProjectSubmission.id == project_id).first(), student)
    db.delete(project)
    db.flush()
    db.refresh(student)
    _recompute(db, student)
    db.commit()
    return MessageResponse(message="Project removed.")


# --------------------------------------------------------------------------- #
#  Research / Experience / Competitions / Leadership (generic create+list+delete)
# --------------------------------------------------------------------------- #
@router.get("/research", response_model=list[ResearchOut])
def my_research(student: Student = Depends(get_current_student)) -> list[ResearchOut]:
    return [ResearchOut.model_validate(r) for r in (student.research_items or [])]


@router.post("/research", response_model=ResearchOut, status_code=status.HTTP_201_CREATED)
def add_my_research(
    payload: ResearchIn,
    db: Session = Depends(get_db),
    student: Student = Depends(get_current_student),
) -> ResearchOut:
    row = ResearchPublication(student_id=student.id, **payload.model_dump())
    db.add(row)
    db.flush()
    db.refresh(student)
    _recompute(db, student)
    db.commit()
    db.refresh(row)
    return ResearchOut.model_validate(row)


@router.delete("/research/{item_id}", response_model=MessageResponse)
def delete_my_research(
    item_id: str,
    db: Session = Depends(get_db),
    student: Student = Depends(get_current_student),
) -> MessageResponse:
    row = _owned(db.query(ResearchPublication).filter(ResearchPublication.id == item_id).first(), student)
    db.delete(row)
    db.flush()
    db.refresh(student)
    _recompute(db, student)
    db.commit()
    return MessageResponse(message="Research item removed.")


@router.get("/experience", response_model=list[ExperienceOut])
def my_experience(student: Student = Depends(get_current_student)) -> list[ExperienceOut]:
    return [ExperienceOut.model_validate(e) for e in (student.experiences or [])]


@router.post("/experience", response_model=ExperienceOut, status_code=status.HTTP_201_CREATED)
def add_my_experience(
    payload: ExperienceIn,
    db: Session = Depends(get_db),
    student: Student = Depends(get_current_student),
) -> ExperienceOut:
    row = Experience(student_id=student.id, **payload.model_dump())
    db.add(row)
    db.flush()
    db.refresh(student)
    _recompute(db, student)
    db.commit()
    db.refresh(row)
    return ExperienceOut.model_validate(row)


@router.delete("/experience/{item_id}", response_model=MessageResponse)
def delete_my_experience(
    item_id: str,
    db: Session = Depends(get_db),
    student: Student = Depends(get_current_student),
) -> MessageResponse:
    row = _owned(db.query(Experience).filter(Experience.id == item_id).first(), student)
    db.delete(row)
    db.flush()
    db.refresh(student)
    _recompute(db, student)
    db.commit()
    return MessageResponse(message="Experience removed.")


@router.get("/competitions", response_model=list[CompetitionOut])
def my_competitions(student: Student = Depends(get_current_student)) -> list[CompetitionOut]:
    return [CompetitionOut.model_validate(c) for c in (student.competitions or [])]


@router.post("/competitions", response_model=CompetitionOut, status_code=status.HTTP_201_CREATED)
def add_my_competition(
    payload: CompetitionIn,
    db: Session = Depends(get_db),
    student: Student = Depends(get_current_student),
) -> CompetitionOut:
    row = Competition(student_id=student.id, **payload.model_dump())
    db.add(row)
    db.flush()
    db.refresh(student)
    _recompute(db, student)
    db.commit()
    db.refresh(row)
    return CompetitionOut.model_validate(row)


@router.delete("/competitions/{item_id}", response_model=MessageResponse)
def delete_my_competition(
    item_id: str,
    db: Session = Depends(get_db),
    student: Student = Depends(get_current_student),
) -> MessageResponse:
    row = _owned(db.query(Competition).filter(Competition.id == item_id).first(), student)
    db.delete(row)
    db.flush()
    db.refresh(student)
    _recompute(db, student)
    db.commit()
    return MessageResponse(message="Competition removed.")


@router.get("/leadership", response_model=list[LeadershipOut])
def my_leadership(student: Student = Depends(get_current_student)) -> list[LeadershipOut]:
    return [LeadershipOut.model_validate(le) for le in (student.leadership_items or [])]


@router.post("/leadership", response_model=LeadershipOut, status_code=status.HTTP_201_CREATED)
def add_my_leadership(
    payload: LeadershipIn,
    db: Session = Depends(get_db),
    student: Student = Depends(get_current_student),
) -> LeadershipOut:
    row = LeadershipActivity(student_id=student.id, **payload.model_dump())
    db.add(row)
    db.flush()
    db.refresh(student)
    _recompute(db, student)
    db.commit()
    db.refresh(row)
    return LeadershipOut.model_validate(row)


@router.delete("/leadership/{item_id}", response_model=MessageResponse)
def delete_my_leadership(
    item_id: str,
    db: Session = Depends(get_db),
    student: Student = Depends(get_current_student),
) -> MessageResponse:
    row = _owned(db.query(LeadershipActivity).filter(LeadershipActivity.id == item_id).first(), student)
    db.delete(row)
    db.flush()
    db.refresh(student)
    _recompute(db, student)
    db.commit()
    return MessageResponse(message="Leadership item removed.")


# --------------------------------------------------------------------------- #
#  Achievements (PRS §5 — awards, certifications, scholarships, grants, …)
# --------------------------------------------------------------------------- #
@router.get("/achievements", response_model=list[AchievementOut])
def my_achievements(student: Student = Depends(get_current_student)) -> list[AchievementOut]:
    return [AchievementOut.model_validate(a) for a in (student.achievements or [])]


@router.post("/achievements", response_model=AchievementOut, status_code=status.HTTP_201_CREATED)
async def add_my_achievement(
    type: AchievementType = Form(...),
    title: str = Form(...),
    description: str | None = Form(default=None),
    link: str | None = Form(default=None),
    evidence: UploadFile | None = File(default=None),
    db: Session = Depends(get_db),
    student: Student = Depends(get_current_student),
) -> AchievementOut:
    evidence_url = None
    if evidence:
        validate_upload(evidence, allowed=ALLOWED_DOC | ALLOWED_PDF | ALLOWED_IMAGE)
        evidence_url = file_storage.save_upload(evidence, subdir=f"achievements/{student.id}")
    row = Achievement(
        student_id=student.id,
        type=type,
        points=ACHIEVEMENT_POINTS.get(type, 0),
        title=title.strip(),
        description=(description or "").strip() or None,
        link=(link or "").strip() or None,
        evidence_url=evidence_url,
        verification_status=VerificationStatus.UNVERIFIED,
    )
    db.add(row)
    db.flush()
    db.refresh(student)
    _recompute(db, student)
    db.commit()
    db.refresh(row)
    return AchievementOut.model_validate(row)


@router.delete("/achievements/{item_id}", response_model=MessageResponse)
def delete_my_achievement(
    item_id: str,
    db: Session = Depends(get_db),
    student: Student = Depends(get_current_student),
) -> MessageResponse:
    row = _owned(db.query(Achievement).filter(Achievement.id == item_id).first(), student)
    db.delete(row)
    db.flush()
    db.refresh(student)
    _recompute(db, student)
    db.commit()
    return MessageResponse(message="Achievement removed.")
