"""Student dashboard computation (PRS §11) — score, ranks, profile completion,
missing-info prompts, improvement recommendations, badges, matched opportunities.
"""
from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.achievement import VerificationStatus
from app.models.badge import BADGE_EMOJI, BADGE_LABELS
from app.models.notification import Notification
from app.models.opportunity import Opportunity
from app.models.opportunity_match import OpportunityMatch
from app.models.student import Student
from app.schemas.me import (
    BadgeOut,
    DashboardOut,
    OpportunityMatchBrief,
    Recommendation,
    ScoreComponents,
)
from app.services import badge_service, scoring_config

_VERIFIED = VerificationStatus.VERIFIED


def _uses_project_model(student: Student) -> bool:
    from app.services.evaluation_engine import uses_project_model

    return uses_project_model(student.field.slug if student.field else None)


def score_components(student: Student, weights: dict[str, float]) -> ScoreComponents:
    return ScoreComponents(
        model="project" if _uses_project_model(student) else "profile",
        academic=student.academic_score,
        project=student.project_score,
        achievement=student.achievement_score,
        profile=student.profile_score,
        research=student.research_score,
        leadership=student.leadership_score,
        experience=student.experience_score,
        competition=student.competition_score,
        final=student.final_score,
        weights=weights,
    )


def _all_items(student: Student) -> list:
    return [
        *(student.research_items or []),
        *(student.experiences or []),
        *(student.competitions or []),
        *(student.leadership_items or []),
        *(student.achievements or []),
    ]


def _completion(student: Student) -> tuple[int, list[str]]:
    checks: list[tuple[bool, str]] = [
        (bool(student.avatar_url), "Add a profile picture"),
        (bool(student.bio), "Write a short bio"),
        (bool(student.course), "Add your course/degree"),
        (student.raw_cgpa is not None or student.raw_gpa is not None, "Add your CGPA"),
        (bool(student.skills), "List your skills"),
        (bool(student.linkedin_url), "Add your LinkedIn"),
        (bool(student.resume_url), "Upload your CV/résumé"),
    ]
    if _uses_project_model(student):
        checks.append((bool(student.projects), "Add at least one project"))
        checks.append(
            (bool(_all_items(student)), "Add research, experience, a competition or an achievement")
        )
    else:
        checks.append(
            (
                bool((student.profile_statement or "").strip()),
                "Describe your accomplishments in the Profile Assessment",
            )
        )
    done = sum(1 for ok, _ in checks if ok)
    missing = [label for ok, label in checks if not ok]
    return round(done / len(checks) * 100), missing


def apply_ready(student: Student) -> tuple[bool, list[str]]:
    """Whether a student's profile is complete enough to apply to opportunities.

    The essentials that make an application meaningful — CGPA, course, a bio, and
    the field's main scored input (a project for Technology/Music, or the Profile
    Assessment for other fields). Returns (ok, missing[])."""
    missing: list[str] = []
    if student.raw_cgpa is None and student.raw_gpa is None:
        missing.append("your CGPA")
    if not student.course:
        missing.append("your course")
    if not (student.bio or "").strip():
        missing.append("a short bio")
    if _uses_project_model(student):
        if not student.projects:
            missing.append("at least one project")
    elif not (student.profile_statement or "").strip():
        missing.append("your Achievements & Profile Assessment")
    return (len(missing) == 0, missing)


def _recommendations(student: Student) -> list[Recommendation]:
    recs: list[Recommendation] = []
    if _uses_project_model(student):
        if not student.projects:
            recs.append(Recommendation(
                title="Add a project",
                detail="Projects are AI-scored out of 40 — the biggest component after academics. "
                       "Add your best project (Music students: add your portfolio).",
                action="/student/profile",
            ))
        if not _all_items(student):
            recs.append(Recommendation(
                title="Add achievements",
                detail="Verified achievements, research, experience and competitions make up your "
                       "Achievements score (out of 20).",
                action="/student/profile",
            ))
    else:
        if not (student.profile_statement or "").strip():
            recs.append(Recommendation(
                title="Complete your Profile Assessment",
                detail="Describe your accomplishments — leadership, internships, awards, research and "
                       "more. The AI scores it out of 60.",
                action="/student/profile",
            ))
        elif student.profile_score <= 0:
            recs.append(Recommendation(
                title="Get your profile assessed",
                detail="Save your Profile Assessment to have the AI score it out of 60.",
                action="/student/profile",
            ))
    if student.raw_cgpa is None and student.raw_gpa is None:
        recs.append(Recommendation(
            title="Add your CGPA",
            detail="Academic performance is worth up to 40 points — the biggest single component.",
            action="/student/profile",
        ))
    return recs[:5]


def _badges(db: Session, student: Student) -> list[BadgeOut]:
    rows = badge_service.sync_badges(db, student)
    return [
        BadgeOut(
            badge_key=b.badge_key,
            label=BADGE_LABELS.get(b.badge_key, b.badge_key),
            emoji=BADGE_EMOJI.get(b.badge_key, "🏅"),
            is_auto=b.is_auto,
        )
        for b in rows
    ]


def _opportunity_matches(db: Session, student: Student, limit: int = 5) -> list[OpportunityMatchBrief]:
    rows = (
        db.query(OpportunityMatch, Opportunity)
        .join(Opportunity, Opportunity.id == OpportunityMatch.opportunity_id)
        .filter(OpportunityMatch.student_id == student.id, Opportunity.is_active.is_(True))
        .order_by(OpportunityMatch.score.desc())
        .limit(limit)
        .all()
    )
    return [
        OpportunityMatchBrief(
            opportunity_id=opp.id,
            title=opp.title,
            organization=opp.organization,
            type=opp.type.value,
            score=match.score,
            reasoning=match.reasoning,
        )
        for match, opp in rows
    ]


def build_dashboard(db: Session, student: Student) -> DashboardOut:
    weights = scoring_config.get_weights(db)
    completion, missing = _completion(student)

    items = _all_items(student)
    verified = sum(1 for i in items if getattr(i, "verification_status", None) == _VERIFIED)
    pending = len(items) - verified

    unread = 0
    if student.user_id:
        unread = (
            db.query(Notification)
            .filter(Notification.user_id == student.user_id, Notification.is_read.is_(False))
            .count()
        )

    return DashboardOut(
        student_id=student.id,
        full_name=student.full_name,
        avatar_url=student.avatar_url,
        final_score=student.final_score,
        scores=score_components(student, weights),
        overall_rank=student.overall_rank,
        field_rank=student.field_rank,
        university_rank=student.university_rank,
        field_name=student.field.name if student.field else None,
        university_name=student.university.name if student.university else None,
        approval_status=student.approval_status,
        is_publicly_visible=student.is_publicly_visible,
        profile_completion=completion,
        verified_items=verified,
        pending_items=pending,
        missing_info=missing,
        recommendations=_recommendations(student),
        badges=_badges(db, student),
        opportunity_matches=_opportunity_matches(db, student),
        unread_notifications=unread,
    )
