"""Shared builder for the full student profile (PRS §9) used by both the
self-service ``/me`` surface and the public ``/students/{id}/full`` endpoint.

``include_contact`` gates the *direct contact* channels (email / phone /
WhatsApp) behind approved-employer/staff access (PRS §16). Professional links
(LinkedIn, portfolio, GitHub, etc.) are part of the public professional profile.
"""
from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.badge import BADGE_EMOJI, BADGE_LABELS
from app.models.student import Student
from app.schemas.achievement import AchievementOut
from app.schemas.competition import CompetitionOut
from app.schemas.experience import ExperienceOut
from app.schemas.leadership import LeadershipOut
from app.schemas.me import BadgeOut, StudentMeOut
from app.schemas.project import ProjectSubmissionOut
from app.schemas.research import ResearchOut
from app.services import scoring_config, student_dashboard


def build_student_out(db: Session, student: Student, *, include_contact: bool) -> StudentMeOut:
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
        email=student.email if include_contact else None,
        avatar_url=student.avatar_url,
        resume_url=student.resume_url,
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
        phone_number=student.phone_number if include_contact else None,
        whatsapp_number=student.whatsapp_number if include_contact else None,
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
