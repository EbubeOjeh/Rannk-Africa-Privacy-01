"""Platform-wide analytics + dashboard stats."""
from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.api.deps import require_super_admin
from app.db.session import get_db
from app.models.field import Field
from app.models.student import Student
from app.models.university import University
from app.models.user import User
from app.schemas.ranking import PlatformStats

router = APIRouter()


@router.get("/platform", response_model=PlatformStats)
def platform_stats(db: Session = Depends(get_db)) -> PlatformStats:
    total_students = db.query(func.count(Student.id)).scalar() or 0
    total_universities = db.query(func.count(University.id)).scalar() or 0
    total_fields = db.query(func.count(Field.id)).scalar() or 0

    top_student = (
        db.query(Student)
        .options(joinedload(Student.university))
        .filter(Student.is_publicly_visible.is_(True))
        .order_by(Student.final_score.desc())
        .first()
    )
    # Blank until a university actually has evaluated students (avg_score > 0),
    # so the stat mirrors "top_student" and doesn't surface a seeded school
    # before any ranking has run.
    top_university = (
        db.query(University)
        .filter(University.avg_score > 0)
        .order_by(University.avg_score.desc(), University.elite_student_count.desc())
        .first()
    )
    return PlatformStats(
        total_students=total_students,
        total_universities=total_universities,
        total_fields=total_fields,
        top_student_name=top_student.full_name if top_student else None,
        top_student_score=top_student.final_score if top_student else None,
        top_student_university=top_student.university.name if top_student and top_student.university else None,
        top_university_name=top_university.name if top_university else None,
        top_university_avg_score=top_university.avg_score if top_university else None,
        top_university_student_count=top_university.student_count if top_university else None,
    )


@router.get("/dashboard")
def admin_dashboard(
    db: Session = Depends(get_db),
    user: User = Depends(require_super_admin),
):
    student_q = db.query(Student)
    return {
        "students_total": student_q.count(),
        "avg_score": float(student_q.with_entities(func.avg(Student.final_score)).scalar() or 0.0),
        "top_score": float(student_q.with_entities(func.max(Student.final_score)).scalar() or 0.0),
        "elite_count": student_q.filter(Student.final_score >= 80.0).count(),
        "score_scale": 100,
        "pending_approvals": student_q.filter(Student.approval_status == "pending").count(),
    }
