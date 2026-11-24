"""Schemas for CEO/admin-created dummy test accounts (auto-deleted after 20 days)."""
from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, EmailStr, Field

TestAccountType = Literal["student", "recruiter", "school_admin"]


class TestAccountCreate(BaseModel):
    account_type: TestAccountType
    name: str = Field(min_length=2, max_length=160)
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)
    # Student / school-admin: the university to attach to (defaults to the first
    # university if omitted for a student).
    university_id: str | None = None
    # Recruiter: the organization name (defaults to the account name).
    organization: str | None = Field(default=None, max_length=200)
    # Student: optional course, auto-mapped to a ranking field.
    course: str | None = Field(default=None, max_length=200)


class TestAccountOut(BaseModel):
    id: str
    account_type: str
    name: str
    email: str
    role: str
    is_active: bool
    approval_status: str | None = None
    organization: str | None = None
    university_name: str | None = None
    created_at: datetime
    expires_at: datetime
    days_left: int

    model_config = {"from_attributes": True}
