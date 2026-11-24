"""Verification badge automation (PRS §14).

Recomputes a student's auto-awarded badges from their verified evidence.
Admin-granted badges (``is_auto = False``) are preserved.
"""
from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.achievement import Achievement, AchievementType, VerificationStatus
from app.models.badge import (
    COMPETITION_WINNER,
    INTERNSHIP_VERIFIED,
    SCHOLARSHIP_RECIPIENT,
    VERIFIED_MUSIC,
    VERIFIED_RESEARCH,
    VERIFIED_STUDENT,
    StudentBadge,
)
from app.models.competition import CompetitionResult
from app.models.experience import ExperienceType
from app.models.research import ResearchPublication
from app.models.student import ApprovalStatus, Student

_VERIFIED = VerificationStatus.VERIFIED


def _qualified_badges(student: Student) -> set[str]:
    badges: set[str] = set()
    achievements = student.achievements or []

    if student.approval_status == ApprovalStatus.APPROVED:
        badges.add(VERIFIED_STUDENT)

    research_ok = any(r.verification_status == _VERIFIED for r in (student.research_items or []))
    research_ok = research_ok or any(
        a.type == AchievementType.PUBLICATION and a.verification_status == _VERIFIED
        for a in achievements
    )
    if research_ok:
        badges.add(VERIFIED_RESEARCH)

    intern_ok = any(
        e.type == ExperienceType.INTERNSHIP and e.verification_status == _VERIFIED
        for e in (student.experiences or [])
    )
    intern_ok = intern_ok or any(
        a.type == AchievementType.INTERNSHIP and a.verification_status == _VERIFIED
        for a in achievements
    )
    if intern_ok:
        badges.add(INTERNSHIP_VERIFIED)

    field_slug = student.field.slug if student.field else None
    if field_slug == "music" and student.music_url and student.approval_status == ApprovalStatus.APPROVED:
        badges.add(VERIFIED_MUSIC)

    winner_ok = any(
        c.result == CompetitionResult.WINNER and c.verification_status == _VERIFIED
        for c in (student.competitions or [])
    )
    winner_ok = winner_ok or any(
        a.type == AchievementType.HACKATHON_WIN and a.verification_status == _VERIFIED
        for a in achievements
    )
    if winner_ok:
        badges.add(COMPETITION_WINNER)

    if any(a.type == AchievementType.SCHOLARSHIP and a.verification_status == _VERIFIED for a in achievements):
        badges.add(SCHOLARSHIP_RECIPIENT)

    return badges


def sync_badges(db: Session, student: Student) -> list[StudentBadge]:
    """Add newly-qualified auto badges, remove auto badges no longer earned."""
    qualified = _qualified_badges(student)
    existing = {b.badge_key: b for b in (student.badges or [])}

    for key in qualified:
        if key not in existing:
            db.add(StudentBadge(student_id=student.id, badge_key=key, is_auto=True))

    for key, badge in existing.items():
        if badge.is_auto and key not in qualified:
            db.delete(badge)

    db.flush()
    return db.query(StudentBadge).filter(StudentBadge.student_id == student.id).all()
