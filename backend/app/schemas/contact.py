"""Contact relay Pydantic schemas."""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

from app.models.contact_message import ContactMessageStatus


class ContactSubmit(BaseModel):
    sender_name: str = Field(min_length=2, max_length=160)
    sender_email: EmailStr
    sender_organization: str | None = Field(default=None, max_length=200)
    sender_role: str | None = Field(default=None, max_length=120)
    subject: str = Field(min_length=4, max_length=200)
    message: str = Field(min_length=10, max_length=4000)


class ContactMessageOut(BaseModel):
    id: str
    student_id: str
    sender_name: str
    sender_email: str
    sender_organization: str | None
    sender_role: str | None
    subject: str
    message: str
    status: ContactMessageStatus
    sent_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}
