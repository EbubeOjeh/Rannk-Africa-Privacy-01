"""Employer surface schemas (PRS §12, §10) — company profile, featured
employers, saved candidates, and the recruiter-facing student search card.
"""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class EmployerProfileIn(BaseModel):
    company_name: str = Field(min_length=2, max_length=200)
    logo_url: str | None = None
    website: str | None = None
    about: str | None = None
    industry: str | None = None
    location: str | None = None
    company_size: str | None = None


class EmployerProfileOut(BaseModel):
    id: str
    user_id: str
    company_name: str
    logo_url: str | None
    website: str | None
    about: str | None
    industry: str | None
    location: str | None
    company_size: str | None
    is_featured: bool
    is_verified: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class FeaturedEmployerOut(BaseModel):
    id: str
    company_name: str
    logo_url: str | None
    website: str | None
    industry: str | None

    model_config = {"from_attributes": True}


class SavedCandidateIn(BaseModel):
    notes: str | None = None


class EmployerStudentCard(BaseModel):
    """Recruiter-facing student card — built manually in the endpoint so contact
    fields can be withheld for recruiters who haven't unlocked contact access."""

    id: str
    full_name: str
    avatar_url: str | None
    university_name: str | None = None
    field_name: str | None = None
    field_color: str | None = None
    course: str | None = None
    academic_level: int | None = None
    year_of_study: int | None = None
    final_score: float = 0.0
    overall_rank: int | None = None
    standardized_gpa_4: float | None = None
    skills: list[str] = []
    saved: bool = False
    contact_unlocked: bool = False
    email: str | None = None
    whatsapp_number: str | None = None
    linkedin_url: str | None = None
