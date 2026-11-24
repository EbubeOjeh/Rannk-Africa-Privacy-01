"""The four new PRS v2.0 sub-dimension scorers:

    Research & Publications      (15%)
    Leadership & Extracurricular (10%)
    Internships & Experience     (10%)
    Competitions & Verified Achievements (10%)

Each returns a normalized ratio (0..1); the engine multiplies it by the
configured weight. Legacy ``Achievement`` rows are folded into the right
dimension via ``ACHIEVEMENT_DIMENSION`` so existing data keeps scoring.

Verified items count at full weight; unverified items count at
``PROVISIONAL_FACTOR`` so self-registered students see an indicative score
before review (it firms up once an admin verifies the evidence).
"""
from __future__ import annotations

from dataclasses import dataclass

from app.models.achievement import (
    ACHIEVEMENT_DIMENSION,
    ACHIEVEMENT_POINTS,
    Achievement,
    VerificationStatus,
)
from app.models.competition import RESULT_POINTS, Competition
from app.models.experience import EXPERIENCE_POINTS, Experience
from app.models.leadership import LEADERSHIP_POINTS, LeadershipActivity
from app.models.research import RESEARCH_POINTS, ResearchPublication

PROVISIONAL_FACTOR = 0.4

# Points that correspond to a full (ratio = 1.0) dimension score.
RESEARCH_TARGET = 12.0
LEADERSHIP_TARGET = 8.0
EXPERIENCE_TARGET = 9.0
COMPETITION_TARGET = 10.0


@dataclass
class DimensionOutcome:
    ratio: float            # 0..1
    points: float           # accumulated weighted points
    target: float           # points needed for ratio = 1.0
    verified_count: int
    total_count: int
    breakdown: dict


def _is_verified(item) -> bool:
    return getattr(item, "verification_status", None) == VerificationStatus.VERIFIED


def _factor(verified: bool) -> float:
    return 1.0 if verified else PROVISIONAL_FACTOR


def _achievements_for(achievements: list[Achievement], dimension: str) -> list[Achievement]:
    return [a for a in achievements if ACHIEVEMENT_DIMENSION.get(a.type) == dimension]


def _finalize(points: float, target: float, verified: int, total: int, items: list[dict]) -> DimensionOutcome:
    ratio = min(1.0, points / target) if target > 0 else 0.0
    return DimensionOutcome(
        ratio=round(ratio, 4),
        points=round(points, 2),
        target=target,
        verified_count=verified,
        total_count=total,
        breakdown={"points": round(points, 2), "target": target,
                   "verified": verified, "total": total, "items": items},
    )


def research_dimension(
    research_items: list[ResearchPublication], achievements: list[Achievement]
) -> DimensionOutcome:
    points = 0.0
    verified = total = 0
    items: list[dict] = []
    for r in research_items:
        total += 1
        v = _is_verified(r)
        verified += int(v)
        base = RESEARCH_POINTS.get(r.type, 0)
        citation_bonus = min(2.0, (r.citations or 0) / 25.0)
        gained = (base + citation_bonus) * _factor(v)
        points += gained
        items.append({"id": r.id, "type": r.type.value, "verified": v, "points": round(gained, 2)})
    for a in _achievements_for(achievements, "research"):
        total += 1
        v = _is_verified(a)
        verified += int(v)
        gained = ACHIEVEMENT_POINTS.get(a.type, 0) * _factor(v)
        points += gained
        items.append({"id": a.id, "type": a.type.value, "verified": v, "points": round(gained, 2)})
    return _finalize(points, RESEARCH_TARGET, verified, total, items)


def experience_dimension(
    experiences: list[Experience], achievements: list[Achievement]
) -> DimensionOutcome:
    points = 0.0
    verified = total = 0
    items: list[dict] = []
    for e in experiences:
        total += 1
        v = _is_verified(e)
        verified += int(v)
        base = EXPERIENCE_POINTS.get(e.type, 0)
        duration_bonus = 1.0 if (e.duration_months or 0) >= 6 else 0.0
        gained = (base + duration_bonus) * _factor(v)
        points += gained
        items.append({"id": e.id, "type": e.type.value, "verified": v, "points": round(gained, 2)})
    for a in _achievements_for(achievements, "experience"):
        total += 1
        v = _is_verified(a)
        verified += int(v)
        gained = ACHIEVEMENT_POINTS.get(a.type, 0) * _factor(v)
        points += gained
        items.append({"id": a.id, "type": a.type.value, "verified": v, "points": round(gained, 2)})
    return _finalize(points, EXPERIENCE_TARGET, verified, total, items)


def leadership_dimension(
    leadership_items: list[LeadershipActivity], achievements: list[Achievement]
) -> DimensionOutcome:
    points = 0.0
    verified = total = 0
    items: list[dict] = []
    for lead in leadership_items:
        total += 1
        v = _is_verified(lead)
        verified += int(v)
        gained = LEADERSHIP_POINTS.get(lead.type, 0) * _factor(v)
        points += gained
        items.append({"id": lead.id, "type": lead.type.value, "verified": v, "points": round(gained, 2)})
    for a in _achievements_for(achievements, "leadership"):
        total += 1
        v = _is_verified(a)
        verified += int(v)
        gained = ACHIEVEMENT_POINTS.get(a.type, 0) * _factor(v)
        points += gained
        items.append({"id": a.id, "type": a.type.value, "verified": v, "points": round(gained, 2)})
    return _finalize(points, LEADERSHIP_TARGET, verified, total, items)


def competition_dimension(
    competitions: list[Competition], achievements: list[Achievement]
) -> DimensionOutcome:
    """Competitions & Verified Achievements (PRS §6) — competitions plus awards,
    certifications, scholarships, grants, fellowships and national recognition."""
    points = 0.0
    verified = total = 0
    items: list[dict] = []
    for c in competitions:
        total += 1
        v = _is_verified(c)
        verified += int(v)
        gained = RESULT_POINTS.get(c.result, 2) * _factor(v)
        points += gained
        items.append({"id": c.id, "type": c.type.value, "result": c.result.value,
                      "verified": v, "points": round(gained, 2)})
    for a in _achievements_for(achievements, "competition"):
        total += 1
        v = _is_verified(a)
        verified += int(v)
        gained = ACHIEVEMENT_POINTS.get(a.type, 0) * _factor(v)
        points += gained
        items.append({"id": a.id, "type": a.type.value, "verified": v, "points": round(gained, 2)})
    return _finalize(points, COMPETITION_TARGET, verified, total, items)
