"""Adjustable scoring weights (PRS §13 — "adjust AI scoring weights").

Any signed-in user may read the effective weights (the frontend surfaces the
scoring breakdown); only a Super Admin may change them. Saving new weights
re-ranks every student so the leaderboard reflects the new model at once.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_super_admin
from app.db.session import get_db
from app.models.user import User
from app.services import audit_service, ranking_service, scoring_config

router = APIRouter()


class WeightsIn(BaseModel):
    academic: float | None = None
    research: float | None = None
    project: float | None = None
    leadership: float | None = None
    experience: float | None = None
    competition: float | None = None


@router.get("/weights")
def get_weights(
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
) -> dict:
    return {
        "weights": scoring_config.get_weights(db),
        "defaults": scoring_config.DEFAULT_WEIGHTS,
        "keys": list(scoring_config.WEIGHT_KEYS),
    }


@router.put("/weights", dependencies=[Depends(require_super_admin)])
def update_weights(
    payload: WeightsIn,
    db: Session = Depends(get_db),
    actor: User = Depends(get_current_user),
) -> dict:
    scoring_config.set_weights(db, payload.model_dump(exclude_none=True))
    ranking_service.recompute_all(db)
    audit_service.record(
        db,
        actor=actor,
        action="scoring.weights.update",
        metadata=payload.model_dump(exclude_none=True),
    )
    db.commit()
    return scoring_config.get_weights(db)
