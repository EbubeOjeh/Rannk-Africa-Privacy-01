"""University Pydantic schemas."""
from pydantic import BaseModel, Field


class UniversityBase(BaseModel):
    name: str
    short_name: str | None = None
    country: str = "Nigeria"
    state: str | None = None
    city: str | None = None
    website: str | None = None
    logo_url: str | None = None
    description: str | None = None
    grading_system: str = "5_point"
    accreditation_type: str | None = None
    institution_type: str = "university"  # "university" | "polytechnic"


class UniversityCreate(UniversityBase):
    pass


class UniversityUpdate(BaseModel):
    name: str | None = None
    short_name: str | None = None
    state: str | None = None
    city: str | None = None
    website: str | None = None
    logo_url: str | None = None
    description: str | None = None
    grading_system: str | None = None
    accreditation_type: str | None = None
    institution_type: str | None = None
    tier: int | None = None


class UniversityOut(UniversityBase):
    id: str
    slug: str
    tier: int
    domain: str | None = None
    approval_status: str = "approved"
    avg_score: float
    top_score: float
    student_count: int
    elite_student_count: int
    overall_rank: int | None
    field_tags: list[str] = Field(default_factory=list)

    model_config = {"from_attributes": True}
