"""Opportunity endpoints (PRS §12, §15) — internships, graduate jobs,
scholarships, research, competitions and leadership programs posted by approved
employers/staff and browsable by students with an AI "% match".
"""
from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import (
    can_view_contact,
    get_current_student,
    get_current_user,
    require_contact_access,
    require_super_admin,
)
from app.core.exceptions import ForbiddenError, NotFoundError, ValidationError
from app.db.session import get_db
from app.models.opportunity import Opportunity, OpportunityType
from app.models.opportunity_application import OpportunityApplication
from app.models.opportunity_match import OpportunityMatch
from app.models.student import Student
from app.models.user import User, UserRole
from app.schemas.common import MessageResponse
from app.schemas.opportunity import (
    ApplicantOut,
    ApplicationOut,
    OpportunityIn,
    OpportunityMatchOut,
    OpportunityOut,
    OpportunityUpdate,
)
from app.services import audit_service, opportunity_match_service, student_dashboard

router = APIRouter()


def _to_out(opportunity: Opportunity) -> OpportunityOut:
    out = OpportunityOut.model_validate(opportunity)
    out.field_name = opportunity.field.name if opportunity.field else None
    return out


def _load(db: Session, opportunity_id: str) -> Opportunity:
    row = db.query(Opportunity).filter(Opportunity.id == opportunity_id).first()
    if not row:
        raise NotFoundError("Opportunity not found.")
    return row


def _assert_can_edit(actor: User, opportunity: Opportunity) -> None:
    if opportunity.posted_by_id != actor.id and actor.role != UserRole.SUPER_ADMIN:
        raise ForbiddenError("You can only manage opportunities you posted.")


@router.get("", response_model=list[OpportunityOut])
def list_opportunities(
    db: Session = Depends(get_db),
    type: OpportunityType | None = Query(default=None),
    field_id: str | None = Query(default=None),
    q: str | None = Query(default=None),
    active_only: bool = Query(default=True),
) -> list[OpportunityOut]:
    query = db.query(Opportunity)
    if active_only:
        query = query.filter(Opportunity.is_active.is_(True))
    if type is not None:
        query = query.filter(Opportunity.type == type)
    if field_id:
        query = query.filter(Opportunity.field_id == field_id)
    if q:
        like = f"%{q.strip()}%"
        query = query.filter(
            Opportunity.title.ilike(like) | Opportunity.description.ilike(like)
        )
    rows = (
        query.order_by(
            Opportunity.is_featured.desc(), Opportunity.created_at.desc()
        )
        .limit(100)
        .all()
    )
    return [_to_out(r) for r in rows]


@router.get("/me/recommended", response_model=list[OpportunityMatchOut])
def my_recommended(
    db: Session = Depends(get_db),
    student: Student = Depends(get_current_student),
) -> list[OpportunityMatchOut]:
    """Top opportunities for the signed-in student, by cached AI/heuristic match."""
    opportunity_match_service.rebuild_matches_for_student(db, student)
    rows = (
        db.query(OpportunityMatch, Opportunity)
        .join(Opportunity, OpportunityMatch.opportunity_id == Opportunity.id)
        .filter(
            OpportunityMatch.student_id == student.id,
            Opportunity.is_active.is_(True),
        )
        .order_by(OpportunityMatch.score.desc())
        .limit(10)
        .all()
    )
    return [
        OpportunityMatchOut(
            opportunity=_to_out(opportunity),
            score=m.score,
            reasoning=m.reasoning,
        )
        for m, opportunity in rows
    ]


@router.get("/{opportunity_id}", response_model=OpportunityOut)
def get_opportunity(opportunity_id: str, db: Session = Depends(get_db)) -> OpportunityOut:
    return _to_out(_load(db, opportunity_id))


# --------------------------------------------------------------------------- #
#  Applications (PRS §12) — students apply, admins review applicants
# --------------------------------------------------------------------------- #
def _application_out(row: OpportunityApplication, *, already_applied: bool = False) -> ApplicationOut:
    return ApplicationOut(
        id=row.id,
        opportunity_id=row.opportunity_id,
        student_id=row.student_id,
        status=row.status.value,
        created_at=row.created_at,
        already_applied=already_applied,
    )


@router.post(
    "/{opportunity_id}/apply",
    response_model=ApplicationOut,
    status_code=status.HTTP_201_CREATED,
)
def apply_to_opportunity(
    opportunity_id: str,
    db: Session = Depends(get_db),
    student: Student = Depends(get_current_student),
) -> ApplicationOut:
    """A student applies to an opportunity. Requires a complete RankAfrica
    profile; idempotent (re-applying returns the existing application)."""
    opp = _load(db, opportunity_id)
    if not opp.is_active:
        raise ValidationError("This opportunity is no longer accepting applications.")

    ready, missing = student_dashboard.apply_ready(student)
    if not ready:
        raise ValidationError(
            "Please complete your RankAfrica profile before applying — still needed: "
            + ", ".join(missing)
            + "."
        )

    existing = (
        db.query(OpportunityApplication)
        .filter(
            OpportunityApplication.opportunity_id == opp.id,
            OpportunityApplication.student_id == student.id,
        )
        .first()
    )
    if existing:
        return _application_out(existing, already_applied=True)

    row = OpportunityApplication(opportunity_id=opp.id, student_id=student.id)
    db.add(row)
    db.flush()
    if student.account:
        audit_service.record(
            db,
            actor=student.account,
            action="opportunity.apply",
            entity_type="opportunity",
            entity_id=opp.id,
        )
    db.commit()
    db.refresh(row)
    return _application_out(row)


@router.get("/me/applications", response_model=list[ApplicationOut])
def my_applications(
    db: Session = Depends(get_db),
    student: Student = Depends(get_current_student),
) -> list[ApplicationOut]:
    """The opportunities the signed-in student has applied to (for 'Applied' state)."""
    rows = (
        db.query(OpportunityApplication)
        .filter(OpportunityApplication.student_id == student.id)
        .order_by(OpportunityApplication.created_at.desc())
        .all()
    )
    return [_application_out(r) for r in rows]


@router.get("/{opportunity_id}/applicants", response_model=list[ApplicantOut])
def opportunity_applicants(
    opportunity_id: str,
    db: Session = Depends(get_db),
    actor: User = Depends(require_super_admin),
) -> list[ApplicantOut]:
    """Admin — every student who applied to this opportunity, most recent first."""
    _load(db, opportunity_id)  # 404 if missing
    rows = (
        db.query(OpportunityApplication, Student)
        .join(Student, Student.id == OpportunityApplication.student_id)
        .filter(OpportunityApplication.opportunity_id == opportunity_id)
        .order_by(OpportunityApplication.created_at.desc())
        .all()
    )
    show_contact = can_view_contact(actor)
    return [
        ApplicantOut(
            application_id=app_row.id,
            student_id=s.id,
            full_name=s.full_name,
            avatar_url=s.avatar_url,
            university_name=s.university.name if s.university else None,
            field_name=s.field.name if s.field else None,
            final_score=s.final_score,
            overall_rank=s.overall_rank,
            status=app_row.status.value,
            applied_at=app_row.created_at,
            email=s.email if show_contact else None,
            phone_number=s.phone_number if show_contact else None,
            whatsapp_number=s.whatsapp_number if show_contact else None,
            linkedin_url=s.linkedin_url,
        )
        for app_row, s in rows
    ]


@router.post("", response_model=OpportunityOut, status_code=status.HTTP_201_CREATED)
def create_opportunity(
    payload: OpportunityIn,
    db: Session = Depends(get_db),
    actor: User = Depends(require_contact_access),
) -> OpportunityOut:
    row = Opportunity(
        posted_by_id=actor.id,
        organization=payload.organization or actor.organization,
        type=payload.type,
        title=payload.title,
        description=payload.description,
        location=payload.location,
        requirements=payload.requirements,
        apply_url=payload.apply_url,
        deadline=payload.deadline,
        field_id=payload.field_id,
        min_gpa=payload.min_gpa,
        min_score=payload.min_score,
        graduation_year=payload.graduation_year,
        is_featured=payload.is_featured,
    )
    db.add(row)
    db.flush()
    audit_service.record(
        db,
        actor=actor,
        action="opportunity.create",
        entity_type="opportunity",
        entity_id=row.id,
    )
    db.commit()
    db.refresh(row)
    opportunity_match_service.rebuild_matches_for_opportunity(db, row)
    return _to_out(row)


@router.patch("/{opportunity_id}", response_model=OpportunityOut)
def update_opportunity(
    opportunity_id: str,
    payload: OpportunityUpdate,
    db: Session = Depends(get_db),
    actor: User = Depends(get_current_user),
) -> OpportunityOut:
    row = _load(db, opportunity_id)
    _assert_can_edit(actor, row)
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(row, key, value)
    audit_service.record(
        db,
        actor=actor,
        action="opportunity.update",
        entity_type="opportunity",
        entity_id=row.id,
    )
    db.commit()
    db.refresh(row)
    return _to_out(row)


@router.post("/{opportunity_id}/close", response_model=OpportunityOut)
def close_opportunity(
    opportunity_id: str,
    db: Session = Depends(get_db),
    actor: User = Depends(get_current_user),
) -> OpportunityOut:
    row = _load(db, opportunity_id)
    _assert_can_edit(actor, row)
    row.is_active = False
    row.closed_at = datetime.now(timezone.utc)
    audit_service.record(
        db,
        actor=actor,
        action="opportunity.close",
        entity_type="opportunity",
        entity_id=row.id,
    )
    db.commit()
    db.refresh(row)
    return _to_out(row)


@router.delete("/{opportunity_id}", response_model=MessageResponse)
def delete_opportunity(
    opportunity_id: str,
    db: Session = Depends(get_db),
    actor: User = Depends(get_current_user),
) -> MessageResponse:
    row = _load(db, opportunity_id)
    _assert_can_edit(actor, row)
    audit_service.record(
        db,
        actor=actor,
        action="opportunity.delete",
        entity_type="opportunity",
        entity_id=row.id,
    )
    db.delete(row)
    db.commit()
    return MessageResponse(message="Opportunity deleted.")
