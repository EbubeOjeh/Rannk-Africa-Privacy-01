"""Experience (internships, employment, volunteering, startups) schemas."""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from app.models.achievement import VerificationStatus
from app.models.experience import ExperienceType


class ExperienceIn(BaseModel):
    type: ExperienceType
    organization: str = Field(min_length=2, max_length=200)
    role_title: str | None = None
    location: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    is_current: bool = False
    duration_months: int | None = None
    description: str | None = None
    link: str | None = None


class ExperienceVerify(BaseModel):
    verification_status: VerificationStatus
    rejection_reason: str | None = None


class ExperienceOut(BaseModel):
    id: str
    student_id: str
    type: ExperienceType
    organization: str
    role_title: str | None
    location: str | None
    start_date: str | None
    end_date: str | None
    is_current: bool
    duration_months: int | None
    description: str | None
    link: str | None
    evidence_url: str | None
    verification_status: VerificationStatus
    verified_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}
