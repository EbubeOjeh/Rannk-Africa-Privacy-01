"""Employer surface (PRS §12, §10) — company profile, featured-employers strip,
recruiter student search/filter, and saved-candidate bookmarks.

Profile reads/writes are owner-scoped (EMPLOYER role). Search and saved-candidate
routes require contact access (an APPROVED employer or internal staff); contact
details on each card are only filled in when the viewer may view contact info.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session, joinedload

from app.api.deps import (
    can_view_contact,
    get_current_user,
    require_contact_access,
    require_super_admin,
)
from app.core.exceptions import ForbiddenError, NotFoundError
from app.db.session import get_db
from app.models.employer_profile import EmployerProfile
from app.models.saved_candidate import SavedCandidate
from app.models.student import Student
from app.models.user import User, UserRole
from app.schemas.common import MessageResponse
from app.schemas.employer import (
    EmployerProfileIn,
    EmployerProfileOut,
    EmployerStudentCard,
    FeaturedEmployerOut,
    SavedCandidateIn,
)
from app.services import audit_service

router = APIRouter()


def _card(
    student: Student,
    *,
    saved: bool,
    contact_unlocked: bool,
) -> EmployerStudentCard:
    """Build a recruiter-facing student card, withholding contact details when
    the viewer hasn't unlocked contact access."""
    university = student.university
    field = student.field
    return EmployerStudentCard(
        id=student.id,
        full_name=student.full_name,
        avatar_url=student.avatar_url,
        university_name=university.name if university else None,
        field_name=field.name if field else None,
        field_color=field.color if field else None,
        course=student.course,
        academic_level=student.academic_level,
        year_of_study=student.year_of_study,
        final_score=student.final_score or 0.0,
        overall_rank=student.overall_rank,
        standardized_gpa_4=student.standardized_gpa_4,
        skills=list(student.skills or []),
        saved=saved,
        contact_unlocked=contact_unlocked,
        email=student.email if contact_unlocked else None,
        whatsapp_number=student.whatsapp_number if contact_unlocked else None,
        linkedin_url=student.linkedin_url if contact_unlocked else None,
    )


@router.get("/profile", response_model=EmployerProfileOut)
def get_profile(
    actor: User = Depends(get_current_user),
) -> EmployerProfileOut:
    profile = actor.employer_profile
    if not profile:
        raise NotFoundError("No employer profile yet.")
    return EmployerProfileOut.model_validate(profile)


@router.put("/profile", response_model=EmployerProfileOut)
def upsert_profile(
    payload: EmployerProfileIn,
    db: Session = Depends(get_db),
    actor: User = Depends(get_current_user),
) -> EmployerProfileOut:
    if actor.role != UserRole.EMPLOYER:
        raise ForbiddenError("Only employer accounts can manage a company profile.")
    profile = actor.employer_profile
    data = payload.model_dump()
    if profile is None:
        profile = EmployerProfile(user_id=actor.id, **data)
        db.add(profile)
        action = "employer.profile.create"
    else:
        for key, value in data.items():
            setattr(profile, key, value)
        action = "employer.profile.update"
    db.flush()
    audit_service.record(
        db, actor=actor, action=action, entity_type="employer_profile", entity_id=profile.id
    )
    db.commit()
    db.refresh(profile)
    return EmployerProfileOut.model_validate(profile)


@router.get("/featured", response_model=list[FeaturedEmployerOut])
def list_featured(db: Session = Depends(get_db)) -> list[FeaturedEmployerOut]:
    rows = (
        db.query(EmployerProfile)
        .filter(EmployerProfile.is_featured.is_(True))
        .order_by(EmployerProfile.created_at.desc())
        .limit(24)
        .all()
    )
    return [FeaturedEmployerOut.model_validate(r) for r in rows]


@router.get("/search")
def search_students(
    db: Session = Depends(get_db),
    actor: User = Depends(require_contact_access),
    q: str | None = None,
    university_id: str | None = None,
    field_id: str | None = None,
    min_score: float | None = None,
    max_score: float | None = None,
    graduation_year: int | None = None,
    skill: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(24, ge=1, le=100),
) -> dict:
    query = (
        db.query(Student)
        .options(joinedload(Student.university), joinedload(Student.field))
        .filter(Student.is_publicly_visible.is_(True))
    )
    if q:
        query = query.filter(Student.full_name.ilike(f"%{q}%"))
    if university_id:
        query = query.filter(Student.university_id == university_id)
    if field_id:
        query = query.filter(Student.field_id == field_id)
    if min_score is not None:
        query = query.filter(Student.final_score >= min_score)
    if max_score is not None:
        query = query.filter(Student.final_score <= max_score)
    if graduation_year is not None:
        query = query.filter(Student.year_of_study == graduation_year)

    query = query.order_by(Student.final_score.desc())

    if skill:
        # SQLite can't reliably query inside a JSON array, so filter in Python.
        wanted = skill.lower()
        matched = [
            s
            for s in query.all()
            if wanted in [str(item).lower() for item in (s.skills or [])]
        ]
        total = len(matched)
        rows = matched[(page - 1) * page_size : (page - 1) * page_size + page_size]
    else:
        total = query.count()
        rows = query.offset((page - 1) * page_size).limit(page_size).all()

    contact_unlocked = can_view_contact(actor)
    student_ids = [s.id for s in rows]
    saved_ids: set[str] = set()
    if student_ids:
        saved_ids = {
            sid
            for (sid,) in db.query(SavedCandidate.student_id)
            .filter(
                SavedCandidate.employer_id == actor.id,
                SavedCandidate.student_id.in_(student_ids),
            )
            .all()
        }

    items = [
        _card(s, saved=s.id in saved_ids, contact_unlocked=contact_unlocked) for s in rows
    ]
    return {"items": items, "total": total, "page": page, "page_size": page_size}


@router.get("/saved", response_model=list[EmployerStudentCard])
def list_saved(
    db: Session = Depends(get_db),
    actor: User = Depends(require_contact_access),
) -> list[EmployerStudentCard]:
    rows = (
        db.query(SavedCandidate)
        .options(
            joinedload(SavedCandidate.student).joinedload(Student.university),
            joinedload(SavedCandidate.student).joinedload(Student.field),
        )
        .filter(SavedCandidate.employer_id == actor.id)
        .order_by(SavedCandidate.created_at.desc())
        .all()
    )
    contact_unlocked = can_view_contact(actor)
    return [
        _card(sc.student, saved=True, contact_unlocked=contact_unlocked)
        for sc in rows
        if sc.student is not None
    ]


@router.post(
    "/saved/{student_id}",
    response_model=MessageResponse,
    status_code=status.HTTP_201_CREATED,
)
def save_candidate(
    student_id: str,
    payload: SavedCandidateIn,
    db: Session = Depends(get_db),
    actor: User = Depends(require_contact_access),
) -> MessageResponse:
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise NotFoundError("Student not found.")
    existing = (
        db.query(SavedCandidate)
        .filter(
            SavedCandidate.employer_id == actor.id,
            SavedCandidate.student_id == student_id,
        )
        .first()
    )
    if existing is None:
        existing = SavedCandidate(
            employer_id=actor.id, student_id=student_id, notes=payload.notes
        )
        db.add(existing)
        action = "employer.candidate.save"
    else:
        existing.notes = payload.notes
        action = "employer.candidate.update"
    db.flush()
    audit_service.record(
        db, actor=actor, action=action, entity_type="saved_candidate", entity_id=existing.id
    )
    db.commit()
    return MessageResponse(message="Candidate saved.")


@router.delete("/saved/{student_id}", response_model=MessageResponse)
def unsave_candidate(
    student_id: str,
    db: Session = Depends(get_db),
    actor: User = Depends(require_contact_access),
) -> MessageResponse:
    saved = (
        db.query(SavedCandidate)
        .filter(
            SavedCandidate.employer_id == actor.id,
            SavedCandidate.student_id == student_id,
        )
        .first()
    )
    if not saved:
        raise NotFoundError("This candidate is not in your saved list.")
    db.delete(saved)
    audit_service.record(
        db,
        actor=actor,
        action="employer.candidate.unsave",
        entity_type="saved_candidate",
        entity_id=saved.id,
    )
    db.commit()
    return MessageResponse(message="Candidate removed from saved list.")


@router.post(
    "/{user_id}/featured",
    response_model=MessageResponse,
    dependencies=[Depends(require_super_admin)],
)
def set_featured(
    user_id: str,
    db: Session = Depends(get_db),
    actor: User = Depends(get_current_user),
    featured: bool = Query(default=True),
) -> MessageResponse:
    profile = (
        db.query(EmployerProfile).filter(EmployerProfile.user_id == user_id).first()
    )
    if not profile:
        raise NotFoundError("This employer has no profile.")
    profile.is_featured = featured
    audit_service.record(
        db,
        actor=actor,
        action="employer.featured.set",
        entity_type="employer_profile",
        entity_id=profile.id,
    )
    db.commit()
    return MessageResponse(
        message="Employer featured." if featured else "Employer un-featured."
    )
