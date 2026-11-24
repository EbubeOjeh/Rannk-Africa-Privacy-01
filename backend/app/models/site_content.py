"""Editable site content (dashboard-driven CMS).

A single row per page/section ``key`` (e.g. ``"landing"``) holding a free-form
JSON ``data`` document. The public landing page reads it; the CEO and technical
admin edit it from the dashboard. Nothing about the public site is hardcoded —
the frontend ships sensible defaults and merges this document over them, so the
site renders even before anyone has saved an edit.
"""
from __future__ import annotations

from sqlalchemy import JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, UUIDPKMixin


class SiteContent(Base, UUIDPKMixin, TimestampMixin):
    __tablename__ = "site_content"

    # Page/section identifier, e.g. "landing". Unique — one document per key.
    key: Mapped[str] = mapped_column(String(80), unique=True, nullable=False, index=True)
    # The editable content document (arbitrary JSON shaped by the frontend).
    data: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
