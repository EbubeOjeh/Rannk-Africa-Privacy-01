"""Compute & refresh global / scoped rankings."""
from __future__ import annotations

from collections import defaultdict

from sqlalchemy import case, distinct, func
from sqlalchemy.orm import Session, joinedload

from app.core.logging import logger
from app.models.field import Field
from app.models.student import Student
from app.models.university import University
from app.services.evaluation_engine import evaluate_student

# /100 scale: an "elite" student scores 80+ (mirrors the spec's leaderboard cut).
ELITE_THRESHOLD = 80.0
# Field rankings only count students who are publicly visible.
TOTAL_FIELDS = 8


def recompute_all(db: Session) -> dict:
    """Re-evaluate every student and refresh derived ranking columns + university aggregates."""
    students = (
        db.query(Student)
        .options(
            joinedload(Student.university),
            joinedload(Student.field),
            joinedload(Student.achievements),
            joinedload(Student.projects),
            joinedload(Student.research_items),
            joinedload(Student.experiences),
            joinedload(Student.competitions),
            joinedload(Student.leadership_items),
            joinedload(Student.submission_cycle),
        )
        .all()
    )
    for student in students:
        evaluate_student(db, student, persist=False)
    db.flush()

    _assign_ranks(db, students)
    _refresh_universities(db)
    db.commit()

    logger.info("Recomputed rankings for {n} students", n=len(students))
    return {"students_evaluated": len(students)}


def _rank_group(group: list[Student], attr: str) -> None:
    """Assign standard competition ranks (1, 2, 2, 4) to one group of students.

    Two properties matter here, and the previous implementation had neither:

    * **Ties share a rank.** Students on an identical score used to receive
      arbitrary sequential ranks, so four students all scoring 38.5 rendered as
      1, 2, 3, 4 — the leaderboard looked ordered by something invisible.
    * **The result is deterministic.** Sorting on score alone over an unordered
      DB fetch meant a recompute with no score changes could silently swap who
      was rank 1. The ``id`` tiebreak pins the order.
    """
    ordered = sorted(group, key=lambda s: (-(s.standardized_score or 0.0), s.id))
    prev_score = object()  # sentinel: never equal to a real score
    rank = 0
    for position, student in enumerate(ordered, start=1):
        score = student.standardized_score or 0.0
        if score != prev_score:
            rank, prev_score = position, score
        setattr(student, attr, rank)


def _assign_ranks(db: Session, students: list[Student]) -> None:
    _rank_group(students, "overall_rank")

    by_field: dict[str | None, list[Student]] = defaultdict(list)
    by_uni: dict[str, list[Student]] = defaultdict(list)
    by_dept: dict[str | None, list[Student]] = defaultdict(list)
    for s in students:
        by_field[s.field_id].append(s)
        by_uni[s.university_id].append(s)
        by_dept[s.department_id].append(s)

    for group in by_field.values():
        _rank_group(group, "field_rank")
    for group in by_uni.values():
        _rank_group(group, "university_rank")
    for group in by_dept.values():
        _rank_group(group, "department_rank")


def _refresh_universities(db: Session) -> None:
    rows = (
        db.query(
            Student.university_id,
            func.count(Student.id),
            func.avg(Student.final_score),
            func.max(Student.final_score),
            func.sum(case((Student.final_score >= ELITE_THRESHOLD, 1), else_=0)),
        )
        .group_by(Student.university_id)
        .all()
    )
    stats = {
        row[0]: dict(student_count=row[1], avg=float(row[2] or 0), top=float(row[3] or 0), elite=int(row[4] or 0))
        for row in rows
    }

    # Distinct fields each university has students in (discipline coverage) —
    # part of the PRS §8 anti-skew formula.
    coverage_rows = (
        db.query(Student.university_id, func.count(distinct(Student.field_id)))
        .filter(Student.field_id.isnot(None))
        .group_by(Student.university_id)
        .all()
    )
    coverage = {row[0]: int(row[1] or 0) for row in coverage_rows}

    unis = db.query(University).all()
    for uni in unis:
        s = stats.get(uni.id, {"student_count": 0, "avg": 0.0, "top": 0.0, "elite": 0})
        uni.student_count = s["student_count"]
        uni.avg_score = round(s["avg"], 1)
        uni.top_score = round(s["top"], 1)
        uni.elite_student_count = s["elite"]

    # PRS §8 overall university ranking — a composite that prevents a single
    # exceptional student from dominating: it is driven by the AVERAGE score,
    # plus the number of top (elite) students, discipline consistency/coverage,
    # and the peak score (smallest weight).
    def _composite(u: University) -> float:
        coverage_pct = (coverage.get(u.id, 0) / TOTAL_FIELDS) * 100.0
        return round(
            0.55 * u.avg_score
            + 0.20 * min(100.0, u.elite_student_count * 12.0)
            + 0.15 * coverage_pct
            + 0.10 * u.top_score,
            3,
        )

    ranked = sorted(unis, key=lambda u: (_composite(u), u.avg_score), reverse=True)
    for i, uni in enumerate(ranked, start=1):
        # Only rank universities that actually have students; others sink to null.
        uni.overall_rank = i if uni.student_count > 0 else None
        if uni.student_count == 0:
            continue
        if i <= 5:
            uni.tier = 1
        elif i <= 12:
            uni.tier = 2
        else:
            uni.tier = 3


def university_field_leaderboard(db: Session, field_key: str, limit: int = 50) -> list[dict]:
    """PRS §8 — per-field university ranking (e.g. "Technology University
    Rankings"). Universities ranked by their publicly-visible students'
    average score *within that field*.
    """
    field = (
        db.query(Field)
        .filter((Field.id == field_key) | (Field.slug == field_key))
        .first()
    )
    if not field:
        return []

    rows = (
        db.query(
            Student.university_id,
            func.count(Student.id),
            func.avg(Student.final_score),
            func.max(Student.final_score),
        )
        .filter(
            Student.field_id == field.id,
            Student.is_publicly_visible.is_(True),
        )
        .group_by(Student.university_id)
        .all()
    )
    uni_ids = [r[0] for r in rows]
    unis = {u.id: u for u in db.query(University).filter(University.id.in_(uni_ids)).all()} if uni_ids else {}

    entries = []
    for uni_id, count, avg, top in rows:
        uni = unis.get(uni_id)
        if not uni:
            continue
        entries.append({
            "university_id": uni_id,
            "university_name": uni.name,
            "university_slug": uni.slug,
            "university_state": uni.state,
            "logo_url": uni.logo_url,
            "tier": uni.tier,
            "overall_rank": uni.overall_rank,
            "field_id": field.id,
            "field_name": field.name,
            "field_slug": field.slug,
            "student_count": int(count or 0),
            "avg_score": round(float(avg or 0), 1),
            "top_score": round(float(top or 0), 1),
        })
    entries.sort(key=lambda e: (e["avg_score"], e["student_count"]), reverse=True)
    for i, e in enumerate(entries[:limit], start=1):
        e["rank"] = i
    return entries[:limit]
