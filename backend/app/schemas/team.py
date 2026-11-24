"""Schemas for the team & dynamic-role management endpoints."""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.models.user import UserRole


class PermissionOut(BaseModel):
    key: str
    label: str
    description: str


class RoleOut(BaseModel):
    id: str
    name: str
    description: str | None = None
    permissions: list[str] = []
    is_system: bool = False
    member_count: int = 0

    model_config = {"from_attributes": True}


class RoleCreate(BaseModel):
    name: str = Field(min_length=2, max_length=80)
    description: str | None = Field(default=None, max_length=300)
    permissions: list[str] = []


class RoleUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=80)
    description: str | None = Field(default=None, max_length=300)
    permissions: list[str] | None = None


class TeamMemberOut(BaseModel):
    id: str
    name: str
    email: EmailStr
    role: UserRole
    title: str | None = None
    avatar_url: str | None = None
    is_active: bool = True
    must_change_password: bool = False
    company_role_id: str | None = None
    company_role_name: str | None = None
    created_at: datetime | None = None

    model_config = {"from_attributes": True}


class TeamCreate(BaseModel):
    name: str = Field(min_length=2, max_length=160)
    email: EmailStr
    role_id: str  # company role to assign
    title: str | None = Field(default=None, max_length=120)

    @field_validator("email")
    @classmethod
    def _company_email(cls, v: str) -> str:
        v = v.lower().strip()
        if not v.endswith("@rankafrica.org"):
            raise ValueError("Team emails must be on the @rankafrica.org domain.")
        return v


class TeamUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=160)
    title: str | None = Field(default=None, max_length=120)
    role_id: str | None = None
    is_active: bool | None = None  # block / unblock


class PublicTeamMember(BaseModel):
    name: str
    title: str | None = None
    avatar_url: str | None = None


class ProfileUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=160)
    title: str | None = Field(default=None, max_length=120)
    avatar_url: str | None = Field(default=None, max_length=500)
