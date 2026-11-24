"""Orchestrator — composes a student's field-specific components into /100.

Per-field model (engine v3):
  * Technology / Music : Academic·40 + Project·40 + Achievements·20
  * All other fields   : Academic·40 + (Achievements & Profile Assessment)·60

Academic uses the in-house WES engine for every field. For Technology/Music the
Project score is the best of the student's AI-rubric-scored projects (a music
portfolio for Music) and Achievements/20 aggregates the verified sub-entities
(research, leadership, experience, competitions). For every OTHER field the /60
comes from the AI assessment of the student's free-text profile statement
(stored in ``student.profile_score``). Recomputing rankings only reads the
stored project/profile scores — no LLM call per recompute.
"""
from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.core.logging import logger
from app.models.evaluation import EvaluationResult
from app.models.student import Student
from app.services import field_mapping
from app.services.evaluation_engine.academic import academic_score
from app.services.evaluation_engine.dimensions import (
    competition_dimension,
    experience_dimension,
    leadership_dimension,
    research_dimension,
)

ENGINE_VERSION = "v3"
ACADEMIC_MAX = 40.0
PROJECT_MAX = 40.0
ACHIEVEMENTS_MAX = 20.0
PROFILE_ASSESSMENT_MAX = 60.0
PROJECT_RUBRIC_MAX = 40.0    # AI project rubric is scored /40
PROFILE_RUBRIC_MAX = 60.0    # AI profile rubric is scored /60
STANDARD_GPA_MAX = 4.0

# Fields that use the project-based model (CGPA/40 + Project/40 + Achievements/20).
# Every other field uses CGPA/40 + Achievements & Profile Assessment/60.
PROJECT_MODEL_SLUGS = {field_mapping.TECHNOLOGY, field_mapping.MUSIC}


def uses_project_model(field_slug: str | None) -> bool:
    return (field_slug or field_mapping.DEFAULT_FIELD) in PROJECT_MODEL_SLUGS


@dataclass
class EvaluationOutcome:
    model: str                 # "project" (Technology/Music) | "profile" (other fields)
    academic_score: float      # /40
    project_score: float       # /40 (0 under the profile model)
    achievement_score: float   # /20 (0 under the profile model)
    profile_score: float       # /60 (0 under the project model)
    final_score: float
    normalized_cgpa: float
    breakdown: dict


class EvaluationEngine:
    """Field-aware orchestrator. Project/profile scores are read from stored
    values (scored separately by the AI) so recomputing rankings stays cheap —
    no LLM call per recompute."""

    def __init__(self, weights: dict[str, float] | None = None, version: str = ENGINE_VERSION):
        # Component maxima are fixed by the field model; ``weights`` is accepted
        # for backwards-compatibility with existing callers but is not used.
        self.version = version

    def evaluate(self, student: Student) -> EvaluationOutcome:
        # --- Academic (WES-style equivalency) — every field ---
        cgpa = student.raw_cgpa if student.raw_cgpa is not None else student.raw_gpa
        uni = student.university
        academic = academic_score(
            cgpa,
            student.gpa_scale or (5.0 if uni and getattr(uni, "institution_type", "university") == "university" else 4.0),
            institution_type=(uni.institution_type if uni and uni.institution_type else "university"),
            tier=(uni.tier if uni else 3),
        )
        student.class_of_degree = academic.class_of_degree
        student.standardized_gpa_4 = academic.standardized_gpa_4
        academic_ratio = min(1.0, (academic.standardized_gpa_4 or 0.0) / STANDARD_GPA_MAX)
        academic_component = round(academic_ratio * ACADEMIC_MAX, 2)

        slug = student.field.slug if student.field else field_mapping.DEFAULT_FIELD
        if slug in PROJECT_MODEL_SLUGS:
            return self._project_model(student, academic, academic_ratio, academic_component, slug)
        return self._profile_model(student, academic, academic_ratio, academic_component, slug)

    def _project_model(self, student, academic, academic_ratio, academic_component, slug) -> EvaluationOutcome:
        # --- Project /40 (best AI-rubric-scored submission; music portfolio for Music) ---
        primary = student.primary_project
        project_ratio = min(1.0, float(primary.total_score) / PROJECT_RUBRIC_MAX) if primary else 0.0
        project_component = round(project_ratio * PROJECT_MAX, 2)
        project_detail = (
            {
                "id": primary.id,
                "title": primary.title,
                "rubric_total": primary.total_score,
                "status": primary.status.value if primary.status else "pending",
                "project_count": len(student.projects or []),
            }
            if primary
            else {"status": "not_submitted"}
        )

        # --- Achievements /20 — aggregate the verified sub-entities ---
        achievements = student.achievements or []
        research = research_dimension(student.research_items or [], achievements)
        leadership = leadership_dimension(student.leadership_items or [], achievements)
        experience = experience_dimension(student.experiences or [], achievements)
        competition = competition_dimension(student.competitions or [], achievements)
        ach_ratio = min(
            1.0, (research.ratio + leadership.ratio + experience.ratio + competition.ratio) / 4.0
        )
        achievement_component = round(ach_ratio * ACHIEVEMENTS_MAX, 2)

        final = round(min(100.0, academic_component + project_component + achievement_component), 2)
        return EvaluationOutcome(
            model="project",
            academic_score=academic_component,
            project_score=project_component,
            achievement_score=achievement_component,
            profile_score=0.0,
            final_score=final,
            normalized_cgpa=academic.standardized_gpa_4,
            breakdown={
                "engine_version": self.version,
                "model": "project",
                "field": slug,
                "maxima": {"academic": ACADEMIC_MAX, "project": PROJECT_MAX, "achievements": ACHIEVEMENTS_MAX},
                "academic": {"ratio": round(academic_ratio, 4), "component": academic_component, **academic.breakdown},
                "project": {"ratio": round(project_ratio, 4), "component": project_component, **project_detail},
                "achievements": {
                    "ratio": round(ach_ratio, 4),
                    "component": achievement_component,
                    "research": research.breakdown,
                    "leadership": leadership.breakdown,
                    "experience": experience.breakdown,
                    "competition": competition.breakdown,
                },
                "final": {"final_score": final, "max": 100.0},
            },
        )

    def _profile_model(self, student, academic, academic_ratio, academic_component, slug) -> EvaluationOutcome:
        # --- Achievements & Profile Assessment /60 (AI-scored free text) ---
        raw_profile = float(student.profile_score or 0.0)
        profile_ratio = min(1.0, raw_profile / PROFILE_RUBRIC_MAX)
        profile_component = round(profile_ratio * PROFILE_ASSESSMENT_MAX, 2)
        has_statement = bool((student.profile_statement or "").strip())

        final = round(min(100.0, academic_component + profile_component), 2)
        return EvaluationOutcome(
            model="profile",
            academic_score=academic_component,
            project_score=0.0,
            achievement_score=0.0,
            profile_score=profile_component,
            final_score=final,
            normalized_cgpa=academic.standardized_gpa_4,
            breakdown={
                "engine_version": self.version,
                "model": "profile",
                "field": slug,
                "maxima": {"academic": ACADEMIC_MAX, "profile_assessment": PROFILE_ASSESSMENT_MAX},
                "academic": {"ratio": round(academic_ratio, 4), "component": academic_component, **academic.breakdown},
                "profile_assessment": {
                    "component": profile_component,
                    "raw_score": round(raw_profile, 2),
                    "max": PROFILE_ASSESSMENT_MAX,
                    "has_statement": has_statement,
                    "status": "evaluated" if raw_profile else ("pending" if has_statement else "not_submitted"),
                },
                "final": {"final_score": final, "max": 100.0},
            },
        )


def evaluate_student(
    db: Session,
    student: Student,
    *,
    persist: bool = True,
    weights: dict[str, float] | None = None,
) -> EvaluationResult:
    """Run the engine and (optionally) persist an :class:`EvaluationResult`.

    Honours per-cycle locking: students whose cycle is CLOSED keep their
    existing scores and we skip recompute. ``weights`` is accepted for
    backwards-compatibility but ignored (component maxima are fixed per field).
    """
    cycle = student.submission_cycle
    if cycle and cycle.is_locked:
        logger.debug("Skipping evaluation for locked cycle student id={id}", id=student.id)
        result = EvaluationResult(
            student_id=student.id,
            engine_version="locked",
            academic_score=student.academic_score,
            project_score=student.project_score,
            achievement_score=student.achievement_score,
            final_score=student.final_score,
            normalized_gpa=student.normalized_cgpa or 0.0,
            standardized_score=student.standardized_score,
            breakdown={"locked": True, "cycle_id": cycle.id},
        )
        if persist:
            db.add(result)
            db.flush()
        return result

    engine = EvaluationEngine()
    outcome = engine.evaluate(student)

    student.academic_score = outcome.academic_score
    student.project_score = outcome.project_score
    student.achievement_score = outcome.achievement_score
    student.profile_score = outcome.profile_score
    # The v3 model folds the old sub-dimensions into Achievements/20; keep the
    # legacy columns at 0 so nothing reads a stale v2.1 value.
    student.research_score = 0.0
    student.leadership_score = 0.0
    student.experience_score = 0.0
    student.competition_score = 0.0
    student.final_score = outcome.final_score
    student.standardized_score = outcome.final_score  # legacy mirror
    student.normalized_cgpa = student.standardized_gpa_4 or outcome.normalized_cgpa

    # For the audit row, achievement_score carries the non-academic/non-project
    # component: the /20 for project-model fields, the /60 for profile-model.
    audit_non_academic = (
        outcome.achievement_score if outcome.model == "project" else outcome.profile_score
    )
    result = EvaluationResult(
        student_id=student.id,
        engine_version=engine.version,
        academic_score=outcome.academic_score,
        project_score=outcome.project_score,
        achievement_score=audit_non_academic,
        final_score=outcome.final_score,
        normalized_gpa=outcome.normalized_cgpa,
        standardized_score=outcome.final_score,
        breakdown=outcome.breakdown,
    )

    if persist:
        db.add(result)
        db.flush()
    logger.debug(
        "Evaluated student id={id} model={m} acad={a} proj={p} ach={ac} profile={pr} final={f}",
        id=student.id, m=outcome.model, a=outcome.academic_score, p=outcome.project_score,
        ac=outcome.achievement_score, pr=outcome.profile_score, f=outcome.final_score,
    )
    return result
