"""Competition schemas."""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from app.models.achievement import VerificationStatus
from app.models.competition import CompetitionResult, CompetitionType


class CompetitionIn(BaseModel):
    type: CompetitionType
    result: CompetitionResult = CompetitionResult.PARTICIPANT
    title: str = Field(min_length=2, max_length=240)
    organizer: str | None = None
    year: int | None = None
    description: str | None = None
    link: str | None = None


class CompetitionVerify(BaseModel):
    verification_status: VerificationStatus
    rejection_reason: str | None = None


class CompetitionOut(BaseModel):
    id: str
    student_id: str
    type: CompetitionType
    result: CompetitionResult
    title: str
    organizer: str | None
    year: int | None
    description: str | None
    link: str | None
    evidence_url: str | None
    verification_status: VerificationStatus
    verified_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}
