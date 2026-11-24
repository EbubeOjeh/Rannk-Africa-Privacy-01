"""Pagination helpers."""
from __future__ import annotations

from math import ceil
from typing import TypeVar

from sqlalchemy.orm import Query

from app.schemas.common import Page, PageMeta

T = TypeVar("T")


def paginate(query: Query, page: int, page_size: int, item_cls):
    total = query.count()
    rows = query.offset((page - 1) * page_size).limit(page_size).all()
    return Page(
        items=[item_cls.model_validate(r) for r in rows],
        meta=PageMeta(
            page=page,
            page_size=page_size,
            total=total,
            total_pages=max(1, ceil(total / page_size)),
        ),
    )
