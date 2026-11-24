"""Public stats + homepage feed (PRS §10) and an admin platform report (§13).

``/public-stats`` and ``/homepage`` are unauthenticated — they drive the public
landing page counters and featured-rankings strips. ``/platform`` is a richer,
admin-only operational snapshot.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.deps import require_super_admin
from app.db.session import get_db
from app.models.achievement import Achievement, VerificationStatus
from app.models.competition import Competition
from app.models.employer_profile import EmployerProfile
from app.models.experience import Experience
from app.models.field import Field
from app.models.leadership import LeadershipActivity
from app.models.opportunity import Opportunity
from app.models.research import ResearchPublication
from app.models.student import Student
from app.models.university import University
from app.models.user import User, UserRole

router = APIRouter()


@router.get("/public-stats")
def public_stats(db: Session = Depends(get_db)) -> dict:
    """Homepage headline counters (PRS §10)."""
    registered_students = (
        db.query(func.count(Student.id))
        .filter(Student.is_publicly_visible.is_(True))
        .scalar()
        or 0
    )
    participating_universities = (
        db.query(func.count(University.id))
        .filter(University.student_count > 0)
        .scalar()
        or 0
    )
    verified_employers = (
        db.query(func.count(EmployerProfile.id))
        .filter(EmployerProfile.is_verified.is_(True))
        .scalar()
        or 0
    )
    available_opportunities = (
        db.query(func.count(Opportunity.id))
        .filter(Opportunity.is_active.is_(True))
        .scalar()
        or 0
    )
    return {
        "registered_students": registered_students,
        "participating_universities": participating_universities,
        "verified_employers": verified_employers,
        "available_opportunities": available_opportunities,
        "successful_placements": 0,
    }


@router.get("/homepage")
def homepage(db: Session = Depends(get_db)) -> dict:
    """Featured rankings + latest opportunities + featured employers (PRS §10)."""
    top_student_row = (
        db.query(Student)
        .filter(Student.is_publicly_visible.is_(True))
        .order_by(Student.final_score.desc())
        .first()
    )
    top_student = None
    if top_student_row:
        top_student = {
            "id": top_student_row.id,
            "full_name": top_student_row.full_name,
            "avatar_url": top_student_row.avatar_url,
            "field_name": top_student_row.field.name if top_student_row.field else None,
            "final_score": top_student_row.final_score,
        }

    # Only surface a "top university" once it actually has evaluated students
    # (avg_score > 0). Seeded universities carry overall_rank but a zero score,
    # so without this guard the homepage would show a school (e.g. the first
    # seeded one) before any student has been ranked. Mirrors "top_student",
    # which requires a publicly visible student.
    top_university_row = (
        db.query(University)
        .filter(University.avg_score > 0)
        .order_by(University.overall_rank.asc().nullslast(), University.avg_score.desc())
        .first()
    )
    top_university = None
    if top_university_row:
        top_university = {
            "id": top_university_row.id,
            "name": top_university_row.name,
            "logo_url": top_university_row.logo_url,
            "avg_score": top_university_row.avg_score,
            "overall_rank": top_university_row.overall_rank,
        }

    top_by_field = []
    for field in db.query(Field).order_by(Field.name).all():
        student = (
            db.query(Student)
            .filter(
                Student.field_id == field.id,
                Student.is_publicly_visible.is_(True),
            )
            .order_by(Student.final_score.desc())
            .first()
        )
        top_by_field.append(
            {
                "field_slug": field.slug,
                "field_name": field.name,
                "student": (
                    {
                        "id": student.id,
                        "full_name": student.full_name,
                        "avatar_url": student.avatar_url,
                        "final_score": student.final_score,
                    }
                    if student
                    else None
                ),
            }
        )

    latest_opportunities = [
        {
            "id": o.id,
            "title": o.title,
            "type": o.type.value if o.type else None,
            "organization": o.organization,
        }
        for o in (
            db.query(Opportunity)
            .filter(Opportunity.is_active.is_(True))
            .order_by(Opportunity.created_at.desc())
            .limit(6)
            .all()
        )
    ]

    featured_employers = [
        {"id": e.id, "company_name": e.company_name, "logo_url": e.logo_url}
        for e in (
            db.query(EmployerProfile)
            .filter(EmployerProfile.is_featured.is_(True))
            .all()
        )
    ]

    return {
        "top_student": top_student,
        "top_university": top_university,
        "top_by_field": top_by_field,
        "latest_opportunities": latest_opportunities,
        "featured_employers": featured_employers,
    }


@router.get("/platform", dependencies=[Depends(require_super_admin)])
def platform_report(db: Session = Depends(get_db)) -> dict:
    """Operational snapshot for the admin dashboard (PRS §13)."""

    def _count(model, *filters) -> int:
        q = db.query(func.count(model.id))
        for f in filters:
            q = q.filter(f)
        return q.scalar() or 0

    def _pending(model) -> int:
        return _count(model, model.verification_status == VerificationStatus.UNVERIFIED)

    totals = {
        "students": _count(Student),
        "publicly_visible_students": _count(Student, Student.is_publicly_visible.is_(True)),
        "universities": _count(University),
        "opportunities": _count(Opportunity),
        "employers": _count(EmployerProfile),
        "pending_verifications": {
            "research": _pending(ResearchPublication),
            "experience": _pending(Experience),
            "competitions": _pending(Competition),
            "leadership": _pending(LeadershipActivity),
            "achievements": _pending(Achievement),
        },
    }

    buckets = [(0, 20), (20, 40), (40, 60), (60, 80), (80, 100)]
    score_distribution = {}
    for low, high in buckets:
        # Top bucket is inclusive of 100; others are [low, high).
        upper_filter = (
            Student.final_score <= high if high == 100 else Student.final_score < high
        )
        score_distribution[f"{low}-{high}"] = _count(
            Student, Student.final_score >= low, upper_filter
        )

    top_students = [
        {
            "id": s.id,
            "full_name": s.full_name,
            "final_score": s.final_score,
            "overall_rank": s.overall_rank,
            "field_name": s.field.name if s.field else None,
            "university_name": s.university.name if s.university else None,
        }
        for s in (
            db.query(Student)
            .order_by(Student.final_score.desc())
            .limit(10)
            .all()
        )
    ]

    top_universities = [
        {
            "id": u.id,
            "name": u.name,
            "overall_rank": u.overall_rank,
            "avg_score": u.avg_score,
            "top_score": u.top_score,
            "student_count": u.student_count,
        }
        for u in (
            db.query(University)
            .filter(University.overall_rank.isnot(None))
            .order_by(University.overall_rank.asc())
            .limit(10)
            .all()
        )
    ]

    return {
        "totals": totals,
        "score_distribution": score_distribution,
        "top_students": top_students,
        "top_universities": top_universities,
    }
