"""Admin verification surface (PRS §13/§14) — verify/reject the four evidence
types that feed the /100 score (research, experience, competitions, leadership).

Verifying or rejecting an item re-scores the owning student (so their leaderboard
position reflects the change immediately) and re-syncs their auto badges.
"""
from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_super_admin
from app.core.exceptions import NotFoundError
from app.db.session import get_db
from app.models.achievement import VerificationStatus
from app.models.competition import Competition
from app.models.experience import Experience
from app.models.leadership import LeadershipActivity
from app.models.research import ResearchPublication
from app.models.user import User
from app.schemas.competition import CompetitionOut, CompetitionVerify
from app.schemas.experience import ExperienceOut, ExperienceVerify
from app.schemas.leadership import LeadershipOut, LeadershipVerify
from app.schemas.research import ResearchOut, ResearchVerify
from app.services import audit_service, badge_service
from app.services.evaluation_engine import evaluate_student

router = APIRouter()


def _verify(db: Session, actor: User, row, payload, *, entity_type: str):
    """Apply a verify/reject decision to an evidence row, re-score & re-badge."""
    row.verification_status = payload.verification_status
    row.rejection_reason = payload.rejection_reason
    row.verified_by_id = actor.id
    row.verified_at = (
        datetime.now(timezone.utc)
        if payload.verification_status == VerificationStatus.VERIFIED
        else None
    )
    db.flush()

    if row.student:
        evaluate_student(db, row.student)
        badge_service.sync_badges(db, row.student)

    audit_service.record(
        db,
        actor=actor,
        action="verification.decision",
        entity_type=entity_type,
        entity_id=row.id,
        metadata={
            "status": payload.verification_status.value,
            "student_id": row.student_id,
        },
    )
    db.commit()
    db.refresh(row)
    return row


@router.post(
    "/research/{item_id}",
    response_model=ResearchOut,
    dependencies=[Depends(require_super_admin)],
)
def verify_research(
    item_id: str,
    payload: ResearchVerify,
    db: Session = Depends(get_db),
    actor: User = Depends(get_current_user),
) -> ResearchOut:
    row = db.query(ResearchPublication).filter(ResearchPublication.id == item_id).first()
    if not row:
        raise NotFoundError("Research item not found.")
    row = _verify(db, actor, row, payload, entity_type="research")
    return ResearchOut.model_validate(row)


@router.post(
    "/experience/{item_id}",
    response_model=ExperienceOut,
    dependencies=[Depends(require_super_admin)],
)
def verify_experience(
    item_id: str,
    payload: ExperienceVerify,
    db: Session = Depends(get_db),
    actor: User = Depends(get_current_user),
) -> ExperienceOut:
    row = db.query(Experience).filter(Experience.id == item_id).first()
    if not row:
        raise NotFoundError("Experience item not found.")
    row = _verify(db, actor, row, payload, entity_type="experience")
    return ExperienceOut.model_validate(row)


@router.post(
    "/competition/{item_id}",
    response_model=CompetitionOut,
    dependencies=[Depends(require_super_admin)],
)
def verify_competition(
    item_id: str,
    payload: CompetitionVerify,
    db: Session = Depends(get_db),
    actor: User = Depends(get_current_user),
) -> CompetitionOut:
    row = db.query(Competition).filter(Competition.id == item_id).first()
    if not row:
        raise NotFoundError("Competition item not found.")
    row = _verify(db, actor, row, payload, entity_type="competition")
    return CompetitionOut.model_validate(row)


@router.post(
    "/leadership/{item_id}",
    response_model=LeadershipOut,
    dependencies=[Depends(require_super_admin)],
)
def verify_leadership(
    item_id: str,
    payload: LeadershipVerify,
    db: Session = Depends(get_db),
    actor: User = Depends(get_current_user),
) -> LeadershipOut:
    row = db.query(LeadershipActivity).filter(LeadershipActivity.id == item_id).first()
    if not row:
        raise NotFoundError("Leadership item not found.")
    row = _verify(db, actor, row, payload, entity_type="leadership")
    return LeadershipOut.model_validate(row)


@router.get("/pending", dependencies=[Depends(require_super_admin)])
def list_pending(
    db: Session = Depends(get_db),
    limit: int = Query(100, ge=1, le=100),
) -> dict:
    """All UNVERIFIED evidence awaiting review, grouped by type (newest first)."""
    research = (
        db.query(ResearchPublication)
        .filter(ResearchPublication.verification_status == VerificationStatus.UNVERIFIED)
        .order_by(ResearchPublication.created_at.desc())
        .limit(limit)
        .all()
    )
    experience = (
        db.query(Experience)
        .filter(Experience.verification_status == VerificationStatus.UNVERIFIED)
        .order_by(Experience.created_at.desc())
        .limit(limit)
        .all()
    )
    competitions = (
        db.query(Competition)
        .filter(Competition.verification_status == VerificationStatus.UNVERIFIED)
        .order_by(Competition.created_at.desc())
        .limit(limit)
        .all()
    )
    leadership = (
        db.query(LeadershipActivity)
        .filter(LeadershipActivity.verification_status == VerificationStatus.UNVERIFIED)
        .order_by(LeadershipActivity.created_at.desc())
        .limit(limit)
        .all()
    )
    return {
        "counts": {
            "research": len(research),
            "experience": len(experience),
            "competitions": len(competitions),
            "leadership": len(leadership),
        },
        "research": [ResearchOut.model_validate(r) for r in research],
        "experience": [ExperienceOut.model_validate(r) for r in experience],
        "competitions": [CompetitionOut.model_validate(r) for r in competitions],
        "leadership": [LeadershipOut.model_validate(r) for r in leadership],
    }
