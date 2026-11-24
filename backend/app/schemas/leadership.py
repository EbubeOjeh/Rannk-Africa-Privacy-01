"""Leadership & Extracurricular schemas."""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from app.models.achievement import VerificationStatus
from app.models.leadership import LeadershipType


class LeadershipIn(BaseModel):
    type: LeadershipType
    title: str = Field(min_length=2, max_length=240)
    organization: str | None = None
    role_title: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    description: str | None = None
    link: str | None = None


class LeadershipVerify(BaseModel):
    verification_status: VerificationStatus
    rejection_reason: str | None = None


class LeadershipOut(BaseModel):
    id: str
    student_id: str
    type: LeadershipType
    title: str
    organization: str | None
    role_title: str | None
    start_date: str | None
    end_date: str | None
    description: str | None
    link: str | None
    evidence_url: str | None
    verification_status: VerificationStatus
    verified_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}
