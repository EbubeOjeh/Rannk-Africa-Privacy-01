"""Pipeline 3 — Achievement Score (/20, hard-capped).

Spec (Step 3.1):
    Internship              3 pts
    Hackathon Participation 2 pts
    Hackathon Win           5 pts
    Leadership Role         5 pts
    Publication             6 pts
    Startup Built           8 pts
Cap: maximum score is 20 points regardless of accumulated total.
Only VERIFIED achievements count toward the score.
"""
from __future__ import annotations

from dataclasses import dataclass

from app.models.achievement import (
    ACHIEVEMENT_CAP,
    ACHIEVEMENT_LABELS,
    ACHIEVEMENT_POINTS,
    Achievement,
    AchievementType,
    VerificationStatus,
)

ACHIEVEMENT_MAX = float(ACHIEVEMENT_CAP)


@dataclass
class AchievementOutcome:
    score: float                       # /20 (capped)
    raw_total: int                     # uncapped total (for transparency)
    counts: dict[str, int]             # type -> number of verified achievements
    breakdown: dict


def achievement_score(achievements: list[Achievement]) -> AchievementOutcome:
    counts: dict[AchievementType, int] = {}
    raw_total = 0
    items: list[dict] = []

    for a in achievements:
        if a.verification_status != VerificationStatus.VERIFIED:
            continue
        counts[a.type] = counts.get(a.type, 0) + 1
        pts = ACHIEVEMENT_POINTS.get(a.type, 0)
        raw_total += pts
        items.append(
            {
                "id": a.id,
                "type": a.type.value,
                "label": ACHIEVEMENT_LABELS.get(a.type, a.type.value),
                "points": pts,
            }
        )

    capped = min(ACHIEVEMENT_MAX, float(raw_total))

    return AchievementOutcome(
        score=round(capped, 2),
        raw_total=raw_total,
        counts={k.value: v for k, v in counts.items()},
        breakdown={
            "verified_items": items,
            "raw_total": raw_total,
            "cap": ACHIEVEMENT_CAP,
            "capped_score": capped,
        },
    )
