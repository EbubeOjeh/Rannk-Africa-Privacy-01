"""Periodic snapshots of computed rankings."""
from __future__ import annotations

from sqlalchemy import JSON, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, UUIDPKMixin


class RankingSnapshot(Base, UUIDPKMixin, TimestampMixin):
    __tablename__ = "ranking_snapshots"

    scope: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    scope_key: Mapped[str | None] = mapped_column(String(120), index=True)
    total_entities: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    payload: Mapped[dict | None] = mapped_column(JSON)
