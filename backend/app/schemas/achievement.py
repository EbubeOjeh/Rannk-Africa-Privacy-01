"""Achievement Pydantic schemas (Pipeline 3)."""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from app.models.achievement import AchievementType, VerificationStatus


class AchievementIn(BaseModel):
    type: AchievementType
    title: str = Field(min_length=2, max_length=240)
    description: str | None = None
    link: str | None = None


class AchievementVerify(BaseModel):
    verification_status: VerificationStatus
    rejection_reason: str | None = None


class AchievementOut(BaseModel):
    id: str
    student_id: str
    type: AchievementType
    points: int
    title: str
    description: str | None
    link: str | None
    evidence_url: str | None
    verification_status: VerificationStatus
    verified_at: datetime | None
    rejection_reason: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class AchievementCatalogItem(BaseModel):
    type: AchievementType
    label: str
    points: int


class AchievementCatalog(BaseModel):
    items: list[AchievementCatalogItem]
    cap: int
