"""AI integrity / fraud-detection suite (PRS §7, §13).

Runs a set of cheap, deterministic heuristics over a Student to surface
integrity concerns (suspicious CGPA, duplicate accounts, duplicate
publications, plagiarised projects) and — when an Anthropic key is configured
— augments project checks with a constrained Claude review. Each finding is
persisted as an :class:`AIFlag` held for manual review before it affects
rankings.

The AI layer is intentionally optional and follows the same guard pattern as
``app/services/evaluation_engine/project_ai.py``: if AI is disabled, the SDK
is missing, or the provider errors, the suite degrades silently to the
deterministic heuristics so the rest of the platform keeps working.
"""
from __future__ import annotations

import json
from typing import Any

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.logging import logger
from app.models.ai_flag import AIFlag, FlagSeverity, FlagStatus, FlagType
from app.models.project_submission import ProjectSubmission
from app.models.student import Student
from app.services import ai_client

# Map the heuristic severity strings to the FlagSeverity enum.
_SEVERITY_MAP: dict[str, FlagSeverity] = {
    "low": FlagSeverity.LOW,
    "medium": FlagSeverity.MEDIUM,
    "high": FlagSeverity.HIGH,
}

AI_SYSTEM_PROMPT = (
    "You are RankAfrica's academic integrity reviewer. You are given a student "
    "project title and description. Decide ONLY whether the project description "
    "shows signs of plagiarism or being copied/AI-generated boilerplate with no "
    "genuine original work. Do not assume missing data. Output ONLY a JSON object "
    'with exactly this shape and no surrounding text:\n'
    '{"plagiarism_suspected": <true|false>, "reason": "<one short sentence>"}'
)


def _norm(text: str | None) -> str:
    """Normalise free text for equality comparison (case/space-insensitive)."""
    return " ".join((text or "").lower().split())


# ---------------------------------------------------------------------------
# Deterministic heuristics
# Each returns a list of finding dicts:
#   {flag_type, severity, reason, entity_type, entity_id, details}
# ---------------------------------------------------------------------------
def check_suspicious_cgpa(student: Student) -> list[dict[str, Any]]:
    """Flag a CGPA that falls outside the bounds of its declared scale."""
    raw = student.raw_cgpa
    if raw is None:
        return []
    scale = student.gpa_scale or 5.0
    out_of_range = raw < 0 or raw > scale or (scale == 5.0 and raw > 5.0)
    if not out_of_range:
        return []
    return [
        {
            "flag_type": FlagType.SUSPICIOUS_CLAIM,
            "severity": "high",
            "reason": f"CGPA {raw} exceeds the {scale} scale",
            "entity_type": "student",
            "entity_id": student.id,
            "details": {"raw_cgpa": raw, "gpa_scale": scale},
        }
    ]


def check_duplicate_account(db: Session, student: Student) -> list[dict[str, Any]]:
    """Flag other students sharing this student's email, or name+university."""
    duplicate_ids: set[str] = set()
    reasons: set[str] = set()

    if student.email:
        email_lc = student.email.strip().lower()
        rows = (
            db.query(Student.id)
            .filter(Student.id != student.id)
            .filter(func.lower(Student.email) == email_lc)
            .all()
        )
        for (other_id,) in rows:
            duplicate_ids.add(other_id)
        if rows:
            reasons.add("same email")

    name_rows = (
        db.query(Student.id)
        .filter(Student.id != student.id)
        .filter(Student.full_name == student.full_name)
        .filter(Student.university_id == student.university_id)
        .all()
    )
    for (other_id,) in name_rows:
        duplicate_ids.add(other_id)
    if name_rows:
        reasons.add("same name + university")

    if not duplicate_ids:
        return []
    return [
        {
            "flag_type": FlagType.DUPLICATE_ACCOUNT,
            "severity": "medium",
            "reason": "Possible duplicate account (" + ", ".join(sorted(reasons)) + ")",
            "entity_type": "student",
            "entity_id": student.id,
            "details": {"duplicate_ids": sorted(duplicate_ids)},
        }
    ]


def check_duplicate_publications(student: Student) -> list[dict[str, Any]]:
    """Flag research items that share a DOI or have an identical title."""
    items = list(student.research_items or [])
    seen_doi: dict[str, str] = {}
    seen_title: dict[str, str] = {}
    findings: list[dict[str, Any]] = []
    flagged: set[str] = set()

    for item in items:
        doi = (item.doi or "").strip().lower()
        title = _norm(item.title)

        match_id: str | None = None
        match_on: str | None = None
        if doi and doi in seen_doi:
            match_id, match_on = seen_doi[doi], "doi"
        elif title and title in seen_title:
            match_id, match_on = seen_title[title], "title"

        if match_id is not None and item.id not in flagged:
            flagged.add(item.id)
            findings.append(
                {
                    "flag_type": FlagType.DUPLICATE_PUBLICATION,
                    "severity": "low",
                    "reason": f"Duplicate publication detected ({match_on}): {item.title}",
                    "entity_type": "research",
                    "entity_id": item.id,
                    "details": {"matches_research_id": match_id, "matched_on": match_on},
                }
            )

        if doi:
            seen_doi.setdefault(doi, item.id)
        if title:
            seen_title.setdefault(title, item.id)

    return findings


def check_plagiarized_projects(db: Session, student: Student) -> list[dict[str, Any]]:
    """Flag projects whose title/description matches another student's project."""
    findings: list[dict[str, Any]] = []
    for project in list(student.projects or []):
        title_lc = _norm(project.title)
        desc_lc = _norm(project.description)

        others = (
            db.query(ProjectSubmission)
            .filter(ProjectSubmission.student_id != student.id)
            .all()
        )
        match = None
        matched_on = None
        for other in others:
            if title_lc and _norm(other.title) == title_lc:
                match, matched_on = other, "title"
                break
            # Simple ">0.9 overlap" proxy: identical normalised description.
            if desc_lc and _norm(other.description) == desc_lc:
                match, matched_on = other, "description"
                break

        if match is not None:
            findings.append(
                {
                    "flag_type": FlagType.PLAGIARIZED_PROJECT,
                    "severity": "medium",
                    "reason": (
                        f"Project '{project.title}' matches another student's "
                        f"submission ({matched_on})"
                    ),
                    "entity_type": "project",
                    "entity_id": project.id,
                    "details": {
                        "matched_project_id": match.id,
                        "matched_student_id": match.student_id,
                        "matched_on": matched_on,
                    },
                }
            )
    return findings


# ---------------------------------------------------------------------------
# Optional AI augmentation
# ---------------------------------------------------------------------------
def ai_review_project(project: ProjectSubmission) -> dict | None:
    """Ask Claude whether a project looks plagiarised.

    Returns ``{"plagiarism_suspected": bool, "reason": str}`` or ``None`` when
    AI is disabled / unavailable / errors (caller falls back to heuristics).
    """
    if not ai_client.ai_configured():
        return None

    user_prompt = (
        f"Project title: {project.title}\n\n"
        f"Description: {project.description}\n\n"
        "Return ONLY the JSON object described in the system prompt."
    )
    try:
        raw = ai_client.complete_json(
            system=AI_SYSTEM_PROMPT,
            user=user_prompt,
            max_tokens=400,
        )
        if raw.startswith("```"):
            raw = raw.strip("`")
            if "\n" in raw:
                raw = raw.split("\n", 1)[1]
            if raw.endswith("```"):
                raw = raw[:-3]
        parsed = json.loads(raw)
    except Exception as exc:  # noqa: BLE001 — degrade gracefully on any error
        logger.error("AI project integrity review failed: {exc}", exc=exc)
        return None

    return {
        "plagiarism_suspected": bool(parsed.get("plagiarism_suspected")),
        "reason": str(parsed.get("reason") or "AI flagged this project as suspicious."),
    }


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------
def scan_student(db: Session, student: Student) -> list[AIFlag]:
    """Run every integrity heuristic (+ optional AI) and persist new flags.

    A flag is only created when no OPEN flag with the same
    ``(student_id, flag_type, entity_id)`` already exists (dedupe). Does not
    commit — the caller is responsible for committing.

    Returns all OPEN flags for the student (existing + newly created).
    """
    ai_used = ai_client.ai_configured()

    findings: list[dict[str, Any]] = []
    findings += check_suspicious_cgpa(student)
    findings += check_duplicate_account(db, student)
    findings += check_duplicate_publications(student)
    findings += check_plagiarized_projects(db, student)

    # AI augmentation: one constrained review per project.
    if ai_used:
        for project in list(student.projects or []):
            verdict = ai_review_project(project)
            if verdict and verdict.get("plagiarism_suspected"):
                findings.append(
                    {
                        "flag_type": FlagType.PLAGIARIZED_PROJECT,
                        "severity": "medium",
                        "reason": verdict.get("reason")
                        or f"AI flagged project '{project.title}' as possibly plagiarised",
                        "entity_type": "project",
                        "entity_id": project.id,
                        "details": {"source": "ai", "project_id": project.id},
                    }
                )

    engine = ai_client.ai_engine_label() if ai_used else "heuristic"

    # Existing OPEN flags for this student — used both for dedupe and the return.
    existing_open = (
        db.query(AIFlag)
        .filter(AIFlag.student_id == student.id)
        .filter(AIFlag.status == FlagStatus.OPEN)
        .all()
    )
    existing_keys = {(f.flag_type, f.entity_id) for f in existing_open}

    created: list[AIFlag] = []
    for finding in findings:
        key = (finding["flag_type"], finding.get("entity_id"))
        if key in existing_keys:
            continue
        existing_keys.add(key)
        flag = AIFlag(
            student_id=student.id,
            entity_type=finding.get("entity_type"),
            entity_id=finding.get("entity_id"),
            flag_type=finding["flag_type"],
            severity=_SEVERITY_MAP.get(finding.get("severity", "medium"), FlagSeverity.MEDIUM),
            status=FlagStatus.OPEN,
            reason=finding["reason"],
            details=finding.get("details"),
            ai_engine=engine,
        )
        db.add(flag)
        created.append(flag)

    db.flush()
    return existing_open + created
