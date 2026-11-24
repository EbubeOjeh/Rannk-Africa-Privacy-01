"""AI integrity flag schemas (PRS §7, §13)."""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel

from app.models.ai_flag import FlagSeverity, FlagStatus, FlagType


class FlagOut(BaseModel):
    id: str
    student_id: str | None
    student_name: str | None = None
    entity_type: str | None
    entity_id: str | None
    flag_type: FlagType
    label: str | None = None
    severity: FlagSeverity
    status: FlagStatus
    reason: str
    details: dict | None
    ai_engine: str | None
    reviewed_at: datetime | None
    review_notes: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class FlagResolve(BaseModel):
    status: FlagStatus  # confirmed or dismissed
    review_notes: str | None = None
