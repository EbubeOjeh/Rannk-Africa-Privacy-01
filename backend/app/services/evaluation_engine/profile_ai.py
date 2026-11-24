"""Achievements & Profile Assessment (/60) via a constrained AI rubric.

For every field EXCEPT Technology and Music, a student's score is
``Academic /40 + Achievements & Profile Assessment /60``. The student writes a
free-text description of their accomplishments (leadership, internships,
volunteering, research, publications, certifications, competitions, awards,
entrepreneurship, community impact, personal statement, …) and this module asks
the AI to score it out of 60 across three equally-weighted /20 categories.

Like ``project_ai.score_project`` it degrades gracefully: if AI is disabled or
the provider errors, it returns ``status="pending"`` with a 0 score so the rest
of the pipeline keeps working, and the student can re-run it once AI is on.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from app.core.logging import logger
from app.models.student import Student
from app.services import ai_client

PROFILE_MAX = 60.0
CATEGORY_MAX = 20.0
CATEGORIES = ("achievements_recognition", "experience_leadership", "impact_distinction")

SYSTEM_PROMPT = (
    "You are RankAfrica's profile evaluator. A student has described their "
    "accomplishments in their own words. Score ONLY the information provided, "
    "across the three categories below (each 0-20). Do not assume or invent "
    "missing data — if a category has little evidence, score it low. Reward "
    "verifiable, specific, high-impact accomplishments over vague claims. "
    "Output strictly JSON.\n\n"
    "Categories (each scored 0-20):\n"
    "  1. Achievements & Recognition — awards, honours, scholarships, grants,\n"
    "       certifications, competitions won, publications.\n"
    "       0-4 none/vague | 5-10 some minor | 11-15 solid verifiable | 16-20 major/prestigious\n"
    "  2. Experience & Leadership — internships, work experience, leadership\n"
    "       roles, entrepreneurship, volunteering, community roles.\n"
    "       0-4 none | 5-10 limited | 11-15 substantial | 16-20 exceptional breadth/seniority\n"
    "  3. Impact & Distinction — research, community impact, measurable outcomes,\n"
    "       and overall distinctiveness of the student's profile.\n"
    "       0-4 none | 5-10 modest | 11-15 clear impact | 16-20 outstanding, wide impact\n\n"
    "Output ONLY a JSON object with exactly this shape and no surrounding text:\n"
    "{\n"
    '  "achievements_recognition": {"score": <int 0-20>, "reasoning": "<one short sentence>"},\n'
    '  "experience_leadership":    {"score": <int 0-20>, "reasoning": "<one short sentence>"},\n'
    '  "impact_distinction":       {"score": <int 0-20>, "reasoning": "<one short sentence>"}\n'
    "}\n"
)


@dataclass
class ProfileOutcome:
    score: float                 # /60
    achievements_recognition: float
    experience_leadership: float
    impact_distinction: float
    reasoning: dict[str, Any]    # raw model output per category
    engine: str
    status: str                  # "evaluated" | "pending" | "empty" | "failed"
    error: str | None = None


def _empty(status: str, engine: str, error: str | None) -> ProfileOutcome:
    return ProfileOutcome(
        score=0.0,
        achievements_recognition=0.0,
        experience_leadership=0.0,
        impact_distinction=0.0,
        reasoning={},
        engine=engine,
        status=status,
        error=error,
    )


def _clamp(value: Any) -> float:
    try:
        n = float(value)
    except (TypeError, ValueError):
        return 0.0
    return max(0.0, min(CATEGORY_MAX, n))


def _parse_json(text: str) -> dict[str, Any]:
    text = text.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if "\n" in text:
            text = text.split("\n", 1)[1]
        if text.endswith("```"):
            text = text[:-3]
    return json.loads(text)


def _build_user_prompt(student: Student) -> str:
    field = getattr(getattr(student, "field", None), "name", None) or "(unspecified)"
    statement = (student.profile_statement or "").strip()
    parts = [
        f"Field of study: {field}",
        f"Course/programme: {student.course or '(not provided)'}",
        "",
        "Student's self-described accomplishments:",
        statement,
        "",
        "Return ONLY the JSON object described in the system prompt. Do not "
        "include explanations, prose, code fences, or trailing commentary.",
    ]
    return "\n".join(parts)


def score_profile(student: Student) -> ProfileOutcome:
    """Score a student's free-text profile statement out of /60."""
    if not (student.profile_statement or "").strip():
        return _empty("empty", "empty", "No profile statement provided yet.")

    if not ai_client.ai_configured():
        return _empty("pending", "disabled", "AI scoring disabled or API key not configured.")

    try:
        raw = ai_client.complete_json(
            system=SYSTEM_PROMPT,
            user=_build_user_prompt(student),
            max_tokens=500,
        )
        parsed = _parse_json(raw)
    except ai_client.AIError as exc:
        logger.warning("AI profile scoring unavailable: {exc}", exc=exc)
        return _empty("pending", "pending", str(exc))
    except Exception as exc:  # noqa: BLE001 — surface any parse/provider error
        logger.error("AI profile scoring failed: {exc}", exc=exc)
        return _empty("failed", ai_client.ai_engine_label(), str(exc))

    achievements = _clamp(parsed.get("achievements_recognition", {}).get("score"))
    experience = _clamp(parsed.get("experience_leadership", {}).get("score"))
    impact = _clamp(parsed.get("impact_distinction", {}).get("score"))
    total = round(achievements + experience + impact, 2)

    return ProfileOutcome(
        score=total,
        achievements_recognition=achievements,
        experience_leadership=experience,
        impact_distinction=impact,
        reasoning=parsed,
        engine=ai_client.ai_engine_label(),
        status="evaluated",
    )
