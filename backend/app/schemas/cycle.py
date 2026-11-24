"""Submission cycle Pydantic schemas."""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from app.models.submission_cycle import CycleStatus


class CycleBase(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    year: int = Field(ge=2000, le=2100)
    submission_opens_at: datetime | None = None
    submission_closes_at: datetime | None = None
    review_ends_at: datetime | None = None
    max_students_per_school: int = Field(default=15, ge=1, le=200)
    description: str | None = None


class CycleCreate(CycleBase):
    pass


class CycleUpdate(BaseModel):
    name: str | None = None
    year: int | None = None
    submission_opens_at: datetime | None = None
    submission_closes_at: datetime | None = None
    review_ends_at: datetime | None = None
    max_students_per_school: int | None = None
    description: str | None = None


class CycleStatusUpdate(BaseModel):
    status: CycleStatus


class CycleOut(CycleBase):
    id: str
    status: CycleStatus
    is_locked: bool
    published_at: datetime | None
    closed_at: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
