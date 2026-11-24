"""Ranking-related schemas."""
from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.student import StudentRow
from app.schemas.university import UniversityOut


class StudentLeaderboard(BaseModel):
    scope: str
    scope_key: str | None = None
    total: int
    rows: list[StudentRow]


class SeasonPublishIn(BaseModel):
    # e.g. "2025/26" — a label for the archived ranking season.
    label: str = Field(min_length=3, max_length=40)


class SeasonOut(BaseModel):
    label: str
    total: int
    published_at: datetime | None = None


class SeasonLeaderboard(BaseModel):
    label: str
    total: int
    published_at: datetime | None = None
    rows: list[StudentRow]


class UniversityLeaderboard(BaseModel):
    total: int
    rows: list[UniversityOut]


class PlatformStats(BaseModel):
    total_students: int
    total_universities: int
    total_fields: int
    top_student_name: str | None
    top_student_score: float | None
    top_student_university: str | None
    top_university_name: str | None
    top_university_avg_score: float | None
    top_university_student_count: int | None
