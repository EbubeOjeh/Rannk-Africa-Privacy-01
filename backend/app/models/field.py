"""Top-level Field/Discipline (Medical, Tech, Law, Accounting, Engineering)."""
from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPKMixin

if TYPE_CHECKING:
    from app.models.department import Department
    from app.models.student import Student


class Field(Base, UUIDPKMixin, TimestampMixin):
    __tablename__ = "fields"

    name: Mapped[str] = mapped_column(String(80), unique=True, nullable=False, index=True)
    slug: Mapped[str] = mapped_column(String(80), unique=True, nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text)
    icon: Mapped[str | None] = mapped_column(String(50))
    color: Mapped[str | None] = mapped_column(String(20))

    students: Mapped[list["Student"]] = relationship(back_populates="field")
    departments: Mapped[list["Department"]] = relationship(back_populates="field")
