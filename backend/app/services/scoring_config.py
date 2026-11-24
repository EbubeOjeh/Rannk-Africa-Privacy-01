"""Adjustable AI scoring weights (PRS §6 framework, §13 "adjust AI scoring weights").

The six component weights sum to 100 by default but are fully tunable by an
admin. They are persisted in the ``site_content`` table under the
``scoring_weights`` key so no schema change is needed to retune the model.

    Academic 40 · Research 15 · Project 15 · Leadership 10 · Experience 10 · Competition 10
"""
from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.site_content import SiteContent

SITE_KEY = "scoring_weights"

WEIGHT_KEYS: tuple[str, ...] = (
    "academic", "research", "project", "leadership", "experience", "competition",
)

DEFAULT_WEIGHTS: dict[str, float] = {
    "academic": 40.0,
    "research": 15.0,
    "project": 15.0,
    "leadership": 10.0,
    "experience": 10.0,
    "competition": 10.0,
}


def get_weights(db: Session) -> dict[str, float]:
    """Return the effective weights, merging any saved overrides over defaults."""
    row = db.query(SiteContent).filter(SiteContent.key == SITE_KEY).first()
    data = (row.data or {}) if row else {}
    weights: dict[str, float] = {}
    for key in WEIGHT_KEYS:
        try:
            weights[key] = float(data.get(key, DEFAULT_WEIGHTS[key]))
        except (TypeError, ValueError):
            weights[key] = DEFAULT_WEIGHTS[key]
    return weights


def set_weights(db: Session, new_weights: dict[str, float]) -> dict[str, float]:
    """Persist (partial) weight overrides. Negative values are clamped to 0."""
    weights = get_weights(db)
    for key in WEIGHT_KEYS:
        if key in new_weights and new_weights[key] is not None:
            weights[key] = max(0.0, float(new_weights[key]))

    row = db.query(SiteContent).filter(SiteContent.key == SITE_KEY).first()
    if row is None:
        row = SiteContent(key=SITE_KEY, data=dict(weights))
        db.add(row)
    else:
        row.data = dict(weights)
    db.commit()
    return weights
