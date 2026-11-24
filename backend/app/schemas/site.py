"""Schemas for the editable site-content (CMS) endpoints."""
from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class SiteContentOut(BaseModel):
    key: str
    data: dict[str, Any] = {}
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class SiteContentUpdate(BaseModel):
    # The full content document for this key. Shape is owned by the frontend
    # (the landing-page editor); the backend stores it verbatim.
    data: dict[str, Any] = Field(default_factory=dict)
