"""Research & Publications schemas."""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from app.models.achievement import VerificationStatus
from app.models.research import ResearchType


class ResearchIn(BaseModel):
    type: ResearchType
    title: str = Field(min_length=2, max_length=300)
    venue: str | None = None
    year: int | None = None
    citations: int = 0
    doi: str | None = None
    link: str | None = None
    description: str | None = None


class ResearchVerify(BaseModel):
    verification_status: VerificationStatus
    rejection_reason: str | None = None


class ResearchOut(BaseModel):
    id: str
    student_id: str
    type: ResearchType
    title: str
    venue: str | None
    year: int | None
    citations: int
    doi: str | None
    link: str | None
    description: str | None
    evidence_url: str | None
    verification_status: VerificationStatus
    verified_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}
