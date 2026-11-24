"""Pipeline 2 — Project Intelligence (/40) via a constrained AI rubric.

Spec (Step 2 — verbatim instruction to the model):
    "Evaluate ONLY using this rubric. Give a score based ONLY on these
    categories, with clear reasoning for each score level. Do not assume
    missing data. Output strictly JSON."

Four categories, each /10:
    Originality       — novelty vs. existing solutions
    Technical Depth   — complexity / sophistication of implementation
    Problem Solving   — relevance + impact of the problem addressed
    Innovation        — degree of disruption / creative advancement

The function is intentionally a small, swappable layer: if no Anthropic API
key is configured (or anthropic SDK isn't installed) the call degrades to
``RubricOutcome(score=0, status="pending", ...)`` so the rest of the
pipeline continues to work in development.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from app.core.config import settings
from app.core.logging import logger
from app.models.project_submission import ProjectSubmission
from app.services import ai_client

PROJECT_MAX = 40.0
CATEGORY_MAX = 10.0
CATEGORIES = ("originality", "technical_depth", "problem_solving", "innovation")

SYSTEM_PROMPT = (
    "You are RankAfrica's project evaluator. Evaluate ONLY using this rubric. "
    "Give a score based ONLY on these categories, with clear reasoning for each "
    "score level. Do not assume missing data. Output strictly JSON.\n\n"
    "Rubric categories (each scored 0-10):\n"
    "  1. Originality       — novelty of idea vs. existing solutions.\n"
    "       0-2 copied / very common  |  3-5 slight improvement on known idea\n"
    "       6-8 new application of existing tech  |  9-10 clearly novel idea or approach\n"
    "  2. Technical Depth   — complexity & sophistication of implementation.\n"
    "       0-2 very simple                       |  3-5 basic coding, limited complexity\n"
    "       6-8 moderate systems, APIs, architecture | 9-10 advanced (AI, distributed, etc.)\n"
    "  3. Problem Solving   — relevance + impact of the problem addressed.\n"
    "       0-2 unclear problem / no solution     |  3-5 minor / academic problem\n"
    "       6-8 real-world useful solution        |  9-10 major scalable real-world problem\n"
    "  4. Innovation        — degree of disruption / creative advancement.\n"
    "       0-2 no innovation                     |  3-5 small improvements\n"
    "       6-8 meaningful innovation             |  9-10 disruptive / new approach\n\n"
    "Output ONLY a JSON object with exactly this shape and no surrounding text:\n"
    "{\n"
    '  "originality":       {"score": <int 0-10>, "reasoning": "<one short sentence>"},\n'
    '  "technical_depth":   {"score": <int 0-10>, "reasoning": "<one short sentence>"},\n'
    '  "problem_solving":   {"score": <int 0-10>, "reasoning": "<one short sentence>"},\n'
    '  "innovation":        {"score": <int 0-10>, "reasoning": "<one short sentence>"}\n'
    "}\n"
)

# Music students submit a portfolio (Spotify / Apple Music / YouTube / SoundCloud
# releases, compositions, music videos, live performances) instead of a software
# project. Same JSON shape / storage columns, music-appropriate rubric.
MUSIC_SYSTEM_PROMPT = (
    "You are RankAfrica's music portfolio evaluator. A Music student has "
    "submitted an original work or portfolio (e.g. Spotify / Apple Music / "
    "SoundCloud releases, YouTube performances, compositions, music videos, live "
    "performances). Evaluate ONLY using this rubric, scoring each category 0-10 "
    "based ONLY on the information provided. Do not assume missing data. Output "
    "strictly JSON.\n\n"
    "Rubric categories (each scored 0-10):\n"
    "  1. originality       — creativity & uniqueness of the music / artistry.\n"
    "  2. technical_depth   — production quality, arrangement and musicianship.\n"
    "  3. problem_solving   — reach & engagement (official releases, streams, plays,\n"
    "       audience) as evidenced by the links provided.\n"
    "  4. innovation        — impact & distinction (awards, notable performances,\n"
    "       influence, creative advancement).\n\n"
    "Output ONLY a JSON object with exactly this shape and no surrounding text:\n"
    "{\n"
    '  "originality":       {"score": <int 0-10>, "reasoning": "<one short sentence>"},\n'
    '  "technical_depth":   {"score": <int 0-10>, "reasoning": "<one short sentence>"},\n'
    '  "problem_solving":   {"score": <int 0-10>, "reasoning": "<one short sentence>"},\n'
    '  "innovation":        {"score": <int 0-10>, "reasoning": "<one short sentence>"}\n'
    "}\n"
)


@dataclass
class RubricOutcome:
    score: float                 # /40
    originality: float
    technical_depth: float
    problem_solving: float
    innovation: float
    reasoning: dict[str, Any]    # raw model output per category
    engine: str
    status: str                  # "evaluated" | "pending" | "failed"
    error: str | None = None


def _build_user_prompt(project: ProjectSubmission, *, is_music: bool = False) -> str:
    if is_music:
        parts = [
            f"Title / release: {project.title}",
            f"About this work: {project.description}",
        ]
        if project.problem_statement:
            parts.append(f"Context / notes: {project.problem_statement}")
    else:
        parts = [
            f"Project title: {project.title}",
            f"Problem statement: {project.problem_statement or '(not provided)'}",
            f"Description: {project.description}",
        ]
    if project.report_url:
        parts.append(f"{'Portfolio / release link' if is_music else 'Report URL'}: {project.report_url}")
    if project.source_code_url:
        parts.append(
            f"{'Streaming link (Spotify/Apple/SoundCloud)' if is_music else 'Source code URL'}: {project.source_code_url}"
        )
    if project.demo_video_url:
        parts.append(f"{'Video (YouTube/performance)' if is_music else 'Demo video URL'}: {project.demo_video_url}")
    parts.append(
        "Return ONLY the JSON object described in the system prompt. Do not "
        "include explanations, prose, code fences, or trailing commentary."
    )
    return "\n\n".join(parts)


def _clamp(value: Any) -> float:
    try:
        n = float(value)
    except (TypeError, ValueError):
        return 0.0
    return max(0.0, min(CATEGORY_MAX, n))


def _parse_rubric_json(text: str) -> dict[str, Any]:
    text = text.strip()
    if text.startswith("```"):
        # Strip fenced code blocks if the model added them despite instructions.
        text = text.strip("`")
        if "\n" in text:
            text = text.split("\n", 1)[1]
        if text.endswith("```"):
            text = text[:-3]
    return json.loads(text)


def score_project(project: ProjectSubmission, *, field_slug: str | None = None) -> RubricOutcome:
    """Score a ProjectSubmission via the configured AI provider.

    ``field_slug='music'`` uses the music-portfolio rubric; any other field uses
    the software/innovation project rubric. Returns a ``RubricOutcome`` with
    ``status="pending"`` when AI is disabled or the SDK is unavailable, so
    callers can persist a placeholder /40 of 0 and re-evaluate later once a key
    is configured.
    """
    is_music = field_slug == "music"
    if not ai_client.ai_configured():
        return RubricOutcome(
            score=0.0,
            originality=0.0,
            technical_depth=0.0,
            problem_solving=0.0,
            innovation=0.0,
            reasoning={},
            engine="disabled",
            status="pending",
            error="AI scoring disabled or API key not configured.",
        )

    try:
        raw = ai_client.complete_json(
            system=MUSIC_SYSTEM_PROMPT if is_music else SYSTEM_PROMPT,
            user=_build_user_prompt(project, is_music=is_music),
            max_tokens=600,
        )
        parsed = _parse_rubric_json(raw)
    except ai_client.AIError as exc:
        logger.warning("AI rubric scoring unavailable: {exc}", exc=exc)
        return RubricOutcome(
            score=0.0,
            originality=0.0,
            technical_depth=0.0,
            problem_solving=0.0,
            innovation=0.0,
            reasoning={},
            engine="pending",
            status="pending",
            error=str(exc),
        )
    except Exception as exc:  # noqa: BLE001 — surface any parse/provider error
        logger.error("AI rubric scoring failed: {exc}", exc=exc)
        return RubricOutcome(
            score=0.0,
            originality=0.0,
            technical_depth=0.0,
            problem_solving=0.0,
            innovation=0.0,
            reasoning={},
            engine=ai_client.ai_engine_label(),
            status="failed",
            error=str(exc),
        )

    originality = _clamp(parsed.get("originality", {}).get("score"))
    technical_depth = _clamp(parsed.get("technical_depth", {}).get("score"))
    problem_solving = _clamp(parsed.get("problem_solving", {}).get("score"))
    innovation = _clamp(parsed.get("innovation", {}).get("score"))
    total = round(originality + technical_depth + problem_solving + innovation, 2)

    return RubricOutcome(
        score=total,
        originality=originality,
        technical_depth=technical_depth,
        problem_solving=problem_solving,
        innovation=innovation,
        reasoning=parsed,
        engine=ai_client.ai_engine_label(),
        status="evaluated",
    )
