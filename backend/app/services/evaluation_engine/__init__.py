"""
RankAfrica Evaluation Engine
============================

A field-specific /100 score (engine v3):

  * Technology / Music : Academic·40 + Project·40 + Achievements·20
  * All other fields   : Academic·40 + (Achievements & Profile Assessment)·60

Modules
-------
- ``academic``      — (CGPA / scale) × 40, WES-style, every field.
- ``project_ai``    — AI rubric for Technology/Music projects (music portfolio
                       for Music), strict JSON, scored /40.
- ``profile_ai``    — AI rubric for the free-text "Achievements & Profile
                       Assessment", scored /60, for all other fields.
- ``achievement``   — Legacy helper (sum of verified achievement points).
- ``engine``        — Field-aware orchestrator + persistence (``evaluate_student``).
- ``grading_systems`` — Helpers to map heterogeneous GPA scales to a 4.0 ratio.
"""
from app.services.evaluation_engine.academic import academic_score
from app.services.evaluation_engine.achievement import achievement_score
from app.services.evaluation_engine.engine import (
    EvaluationEngine,
    EvaluationOutcome,
    evaluate_student,
    uses_project_model,
)
from app.services.evaluation_engine.profile_ai import ProfileOutcome, score_profile
from app.services.evaluation_engine.project_ai import RubricOutcome, score_project

__all__ = [
    "EvaluationEngine",
    "EvaluationOutcome",
    "ProfileOutcome",
    "RubricOutcome",
    "academic_score",
    "achievement_score",
    "evaluate_student",
    "score_profile",
    "score_project",
    "uses_project_model",
]
