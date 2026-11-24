"""Project submission Pydantic schemas (Pipeline 2)."""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from app.models.project_submission import ProjectStatus


class ProjectSubmissionIn(BaseModel):
    title: str = Field(min_length=4, max_length=240)
    description: str = Field(min_length=20)
    problem_statement: str | None = None
    report_url: str | None = None
    source_code_url: str | None = None
    demo_video_url: str | None = None


class ProjectModerationIn(BaseModel):
    originality: float = Field(ge=0, le=10)
    technical_depth: float = Field(ge=0, le=10)
    problem_solving: float = Field(ge=0, le=10)
    innovation: float = Field(ge=0, le=10)
    moderator_notes: str | None = None


class ProjectSubmissionOut(BaseModel):
    id: str
    student_id: str
    title: str
    description: str
    problem_statement: str | None
    report_url: str | None
    source_code_url: str | None
    demo_video_url: str | None

    originality: float
    technical_depth: float
    problem_solving: float
    innovation: float
    total_score: float
    status: ProjectStatus

    ai_engine: str | None
    ai_reasoning: dict | None
    moderator_notes: str | None
    evaluated_at: datetime | None
    moderated_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}
