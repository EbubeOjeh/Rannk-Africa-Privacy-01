"""Field/Discipline schemas."""
from pydantic import BaseModel


class FieldOut(BaseModel):
    id: str
    name: str
    slug: str
    description: str | None = None
    icon: str | None = None
    color: str | None = None
    student_count: int = 0
    top_score: float = 0.0

    model_config = {"from_attributes": True}
