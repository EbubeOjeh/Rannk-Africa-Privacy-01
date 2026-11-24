"""Opportunity + AI-match schemas (PRS §12, §15)."""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from app.models.opportunity import OpportunityType


class OpportunityIn(BaseModel):
    type: OpportunityType
    title: str = Field(min_length=3, max_length=240)
    description: str = Field(min_length=10)
    organization: str | None = None
    location: str | None = None
    requirements: str | None = None
    apply_url: str | None = None
    deadline: str | None = None
    field_id: str | None = None
    min_gpa: float | None = None
    min_score: float | None = None
    graduation_year: int | None = None
    is_featured: bool = False


class OpportunityUpdate(BaseModel):
    type: OpportunityType | None = None
    title: str | None = Field(default=None, min_length=3, max_length=240)
    description: str | None = Field(default=None, min_length=10)
    organization: str | None = None
    location: str | None = None
    requirements: str | None = None
    apply_url: str | None = None
    deadline: str | None = None
    field_id: str | None = None
    min_gpa: float | None = None
    min_score: float | None = None
    graduation_year: int | None = None
    is_featured: bool | None = None


class OpportunityOut(BaseModel):
    id: str
    posted_by_id: str | None
    organization: str | None
    type: OpportunityType
    title: str
    description: str
    location: str | None
    requirements: str | None
    apply_url: str | None
    deadline: str | None
    field_id: str | None
    field_name: str | None = None
    min_gpa: float | None
    min_score: float | None
    graduation_year: int | None
    is_active: bool
    is_featured: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class OpportunityMatchOut(BaseModel):
    opportunity: OpportunityOut
    score: float
    reasoning: str | None = None


class ApplicationOut(BaseModel):
    """A student's application record (returned on apply + in /me/applications)."""
    id: str
    opportunity_id: str
    student_id: str
    status: str
    created_at: datetime
    # True when the student had already applied (apply is idempotent).
    already_applied: bool = False
    message: str = "Your application has been received. We'll notify you if you're selected."


class ApplicantOut(BaseModel):
    """One applicant, for the admin "applicants per opportunity" view."""
    application_id: str
    student_id: str
    full_name: str
    avatar_url: str | None = None
    university_name: str | None = None
    field_name: str | None = None
    final_score: float = 0.0
    overall_rank: int | None = None
    status: str
    applied_at: datetime
    # Contact channels — populated only for viewers allowed to see them.
    email: str | None = None
    phone_number: str | None = None
    whatsapp_number: str | None = None
    linkedin_url: str | None = None
