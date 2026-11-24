"""Student Pydantic schemas."""
from __future__ import annotations

from pydantic import BaseModel, EmailStr, Field

from app.models.student import ApprovalStatus


class StudentBase(BaseModel):
    full_name: str = Field(min_length=2, max_length=180)
    email: EmailStr | None = None
    phone_number: str | None = None
    linkedin_url: str | None = None
    matric_number: str | None = None
    gender: str | None = None
    avatar_url: str | None = None
    academic_level: int | None = None
    bio: str | None = Field(default=None, max_length=1600)
    department_id: str | None = None
    field_id: str | None = None


class StudentCreate(StudentBase):
    university_id: str
    submission_cycle_id: str | None = None
    raw_gpa: float | None = None
    raw_cgpa: float | None = None
    # Most Nigerian universities grade on 5.0; polytechnics on 4.0.
    # The WES engine handles whichever value is passed.
    gpa_scale: float = 5.0
    credits_earned: int = 0


class StudentUpdate(BaseModel):
    full_name: str | None = None
    email: EmailStr | None = None
    phone_number: str | None = None
    linkedin_url: str | None = None
    matric_number: str | None = None
    department_id: str | None = None
    field_id: str | None = None
    academic_level: int | None = None
    bio: str | None = Field(default=None, max_length=1600)
    avatar_url: str | None = None
    raw_gpa: float | None = None
    raw_cgpa: float | None = None
    gpa_scale: float | None = None
    credits_earned: int | None = None


class StudentApprovalIn(BaseModel):
    approval_status: ApprovalStatus
    approval_notes: str | None = None


class StudentScoreBreakdown(BaseModel):
    model: str = "project"          # "project" (Tech/Music) | "profile" (others)
    field_slug: str | None = None
    academic_score: float
    project_score: float
    achievement_score: float
    profile_score: float = 0.0      # /60 for the profile model
    final_score: float
    normalized_cgpa: float | None
    cap: float = 100.0


class StudentOut(StudentBase):
    id: str
    university_id: str
    submission_cycle_id: str | None
    raw_gpa: float | None
    raw_cgpa: float | None
    gpa_scale: float
    normalized_cgpa: float | None = None
    standardized_gpa_4: float | None = None
    class_of_degree: str | None = None
    credits_earned: int

    field_slug: str | None = None
    academic_score: float
    project_score: float
    achievement_score: float
    profile_score: float = 0.0
    final_score: float
    standardized_score: float
    consistency_score: float

    approval_status: ApprovalStatus
    is_publicly_visible: bool

    overall_rank: int | None
    field_rank: int | None
    university_rank: int | None
    department_rank: int | None

    model_config = {"from_attributes": True}


class StudentRow(BaseModel):
    """Compact row for the public ranking tables."""

    id: str
    full_name: str
    avatar_url: str | None = None
    university_id: str
    university_name: str
    university_state: str | None = None
    institution_type: str | None = None
    field_id: str | None = None
    field_name: str | None = None
    field_slug: str | None = None
    field_color: str | None = None
    academic_level: int | None = None
    academic_score: float = 0.0
    project_score: float = 0.0
    achievement_score: float = 0.0
    profile_score: float = 0.0
    final_score: float = 0.0
    standardized_gpa_4: float | None = None
    class_of_degree: str | None = None
    # Legacy alias retained for older frontend code (mirrors final_score).
    standardized_score: float = 0.0
    overall_rank: int | None = None
