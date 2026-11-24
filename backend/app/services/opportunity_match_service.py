"""Opportunity <-> Student compatibility scoring (PRS §15, "% Match").

Two layers, both returning ``(score 0-100, reasoning)``:

* ``rule_based`` — a deterministic heuristic (field/score/GPA/year/skills).
  Always available, no external calls, robust to missing data.
* ``ai_match`` — an optional Claude refinement. Guarded exactly like
  ``evaluation_engine.project_ai``: when ``AI_ENABLED`` is off or no
  ``ANTHROPIC_API_KEY`` is configured (or the SDK/JSON parse fails) it
  returns ``None`` and the caller falls back to the rule-based score.

``match`` is the single entry point: AI first when configured, else rules.
``rebuild_matches_for_*`` upsert cached ``OpportunityMatch`` rows so the
browse list never re-calls the model on every page load.
"""
from __future__ import annotations

import json
import re

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.logging import logger
from app.models.opportunity import Opportunity
from app.models.opportunity_match import OpportunityMatch
from app.models.student import Student
from app.services import ai_client

# --- Heuristic weights (sum to 100) ------------------------------------------
W_FIELD = 40.0        # same discipline as the opportunity
W_SCORE = 20.0        # meets / approaches the min standardized score
W_GPA = 15.0          # meets / approaches the min 4.0-scale GPA
W_YEAR = 10.0         # graduation-year / academic-level alignment
W_SKILLS = 15.0       # skills overlap with requirements/description text

_WORD_RE = re.compile(r"[a-z0-9+#.]+")


def _tokens(text: str | None) -> set[str]:
    if not text:
        return set()
    return {t for t in _WORD_RE.findall(text.lower()) if len(t) >= 3}


def _skill_overlap(student: Student, opportunity: Opportunity) -> tuple[float, int]:
    """Fraction (0-1) of the student's skills that appear (as a case-insensitive
    substring or token) in the opportunity's requirements/description, plus the
    raw count of matched skills."""
    skills = [str(s).strip().lower() for s in (student.skills or []) if str(s).strip()]
    if not skills:
        return 0.0, 0
    haystack = " ".join(
        filter(None, [opportunity.requirements, opportunity.description, opportunity.title])
    ).lower()
    if not haystack:
        return 0.0, 0
    hay_tokens = _tokens(haystack)
    matched = 0
    for skill in skills:
        if skill in haystack or _tokens(skill) & hay_tokens:
            matched += 1
    return matched / len(skills), matched


def rule_based(student: Student, opportunity: Opportunity) -> tuple[float, str]:
    """Deterministic 0-100 compatibility score + a short human reason.

    Robust to ``None`` everywhere: a missing requirement simply doesn't
    contribute (it neither rewards nor penalises beyond its weight)."""
    score = 0.0
    reasons: list[str] = []

    # 1. Field match — the single biggest signal.
    student_field_id = getattr(getattr(student, "field", None), "id", None) or student.field_id
    if opportunity.field_id and student_field_id and student_field_id == opportunity.field_id:
        score += W_FIELD
        reasons.append("field")
    elif not opportunity.field_id:
        # Open to any discipline → award half the field weight so it isn't
        # systematically out-ranked by field-specific posts.
        score += W_FIELD / 2

    # 2. Minimum standardized score.
    if opportunity.min_score is not None:
        final = student.final_score or 0.0
        if final >= opportunity.min_score:
            score += W_SCORE
            reasons.append("score")
        elif opportunity.min_score > 0:
            score += W_SCORE * max(0.0, final / opportunity.min_score)
    else:
        score += W_SCORE  # no bar → fully satisfied

    # 3. Minimum GPA (4.0 scale).
    if opportunity.min_gpa is not None:
        gpa = student.standardized_gpa_4
        if gpa is not None and gpa >= opportunity.min_gpa:
            score += W_GPA
            reasons.append("GPA")
        elif gpa is not None and opportunity.min_gpa > 0:
            score += W_GPA * max(0.0, gpa / opportunity.min_gpa)
    else:
        score += W_GPA

    # 4. Graduation-year / academic-level alignment.
    target_year = opportunity.graduation_year
    if target_year is None:
        score += W_YEAR
    else:
        # Use academic_level (preferred) or year_of_study as a coarse proxy
        # for how close the student is to graduating.
        level = student.academic_level or student.year_of_study
        if level is not None and level >= 3:
            score += W_YEAR
            reasons.append("graduation timing")
        else:
            score += W_YEAR / 2

    # 5. Skills overlap.
    overlap, matched = _skill_overlap(student, opportunity)
    score += W_SKILLS * overlap
    if matched:
        reasons.append("skills")

    score = round(max(0.0, min(100.0, score)), 1)
    reasoning = _summarise(score, reasons)
    return score, reasoning


def _summarise(score: float, reasons: list[str]) -> str:
    if score >= 80:
        prefix = "Strong match"
    elif score >= 55:
        prefix = "Good match"
    elif score >= 30:
        prefix = "Partial match"
    else:
        prefix = "Weak match"
    if reasons:
        return f"{prefix} — aligned on {', '.join(reasons)}."
    return f"{prefix} based on overall profile fit."


# --- Optional Claude refinement ----------------------------------------------
_AI_SYSTEM_PROMPT = (
    "You are RankAfrica's opportunity matcher. Given a student's academic "
    "profile and an opportunity, rate their compatibility from 0 to 100 based "
    "ONLY on the information provided. Do not assume missing data. Output "
    "strictly a JSON object and nothing else, with this exact shape:\n"
    '{"score": <number 0-100>, "reason": "<one short sentence>"}'
)


def _build_ai_prompt(student: Student, opportunity: Opportunity) -> str:
    field_name = getattr(getattr(student, "field", None), "name", None)
    university = getattr(getattr(student, "university", None), "name", None)
    skills = ", ".join(str(s) for s in (student.skills or [])) or "(none listed)"
    parts = [
        "STUDENT",
        f"  Field of study: {field_name or student.course or '(unknown)'}",
        f"  University: {university or '(unknown)'}",
        f"  Standardized GPA (4.0): {student.standardized_gpa_4 if student.standardized_gpa_4 is not None else '(unknown)'}",
        f"  Final score (/100): {student.final_score}",
        f"  Academic level / year: {student.academic_level or student.year_of_study or '(unknown)'}",
        f"  Skills: {skills}",
        "",
        "OPPORTUNITY",
        f"  Type: {opportunity.type.value}",
        f"  Title: {opportunity.title}",
        f"  Organization: {opportunity.organization or '(unspecified)'}",
        f"  Minimum GPA: {opportunity.min_gpa if opportunity.min_gpa is not None else '(none)'}",
        f"  Minimum score: {opportunity.min_score if opportunity.min_score is not None else '(none)'}",
        f"  Target graduation year: {opportunity.graduation_year or '(any)'}",
        f"  Requirements: {opportunity.requirements or '(not provided)'}",
        f"  Description: {opportunity.description}",
        "",
        "Return ONLY the JSON object described in the system prompt.",
    ]
    return "\n".join(parts)


def _clamp_score(value: object) -> float:
    try:
        n = float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return 0.0
    return round(max(0.0, min(100.0, n)), 1)


def _parse_ai_json(text: str) -> dict:
    text = text.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if "\n" in text:
            text = text.split("\n", 1)[1]
        if text.endswith("```"):
            text = text[:-3]
    return json.loads(text)


def ai_match(student: Student, opportunity: Opportunity) -> tuple[float, str] | None:
    """AI-scored compatibility, or ``None`` when AI is unavailable/fails."""
    if not ai_client.ai_configured():
        return None

    try:
        raw = ai_client.complete_json(
            system=_AI_SYSTEM_PROMPT,
            user=_build_ai_prompt(student, opportunity),
            max_tokens=200,
        )
        parsed = _parse_ai_json(raw)
    except Exception as exc:  # noqa: BLE001 — any provider/parse error → fall back
        logger.error("AI opportunity match failed: {exc}", exc=exc)
        return None

    score = _clamp_score(parsed.get("score"))
    reason = str(parsed.get("reason") or "AI-assessed compatibility.").strip()
    return score, reason


def match(student: Student, opportunity: Opportunity) -> tuple[float, str]:
    """Single entry point: Claude refinement when configured, else heuristic."""
    return ai_match(student, opportunity) or rule_based(student, opportunity)


# --- Cache (re)builders -------------------------------------------------------
def _engine_label() -> str:
    if ai_client.ai_configured():
        return ai_client.ai_engine_label()
    return "rule_based"


def _upsert(db: Session, student: Student, opportunity: Opportunity) -> None:
    score, reasoning = match(student, opportunity)
    row = (
        db.query(OpportunityMatch)
        .filter(
            OpportunityMatch.student_id == student.id,
            OpportunityMatch.opportunity_id == opportunity.id,
        )
        .first()
    )
    if row is None:
        row = OpportunityMatch(
            student_id=student.id,
            opportunity_id=opportunity.id,
            score=score,
            reasoning=reasoning,
            engine=_engine_label(),
        )
        db.add(row)
    else:
        row.score = score
        row.reasoning = reasoning
        row.engine = _engine_label()


def rebuild_matches_for_student(db: Session, student: Student) -> int:
    """Recompute this student's match against every active opportunity."""
    opportunities = (
        db.query(Opportunity).filter(Opportunity.is_active.is_(True)).all()
    )
    for opp in opportunities:
        _upsert(db, student, opp)
    db.commit()
    return len(opportunities)


def rebuild_matches_for_opportunity(db: Session, opportunity: Opportunity) -> int:
    """Recompute every publicly-visible student's match against this post."""
    students = (
        db.query(Student).filter(Student.is_publicly_visible.is_(True)).all()
    )
    for student in students:
        _upsert(db, student, opportunity)
    db.commit()
    return len(students)
