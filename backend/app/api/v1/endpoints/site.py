"""Editable site content (dashboard-driven CMS).

Read is public (the landing page fetches it on every visit). Writes are gated on
the ``manage_site`` permission, which only the technical admin (SUPER_ADMIN) and
the CEO (``full_access``) hold by default — they can delegate it to a teammate
from the Team -> Roles editor if they ever choose to.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import require_permission
from app.core.permissions import MANAGE_SITE
from app.db.session import get_db
from app.models.site_content import SiteContent
from app.schemas.site import SiteContentOut, SiteContentUpdate

router = APIRouter()

# Keys the editor is allowed to manage. Keeping an allow-list means a typo in a
# URL can't silently create an orphan document.
#   rankings — the rankings-release switch ({released, message}); see settings_service.
#   the rest — per-page CMS documents edited from the Website editor. The
#   rankings PAGE copy is 'rankings_page' so it doesn't collide with 'rankings'.
ALLOWED_KEYS = {
    "rankings",
    "landing",
    "platform",
    "about",
    "opportunities_page",
    "contact",
    "rankings_page",
    "universities",
    "fields",
    "team",
}


def _get_or_none(db: Session, key: str) -> SiteContent | None:
    return db.query(SiteContent).filter(SiteContent.key == key).first()


@router.get("/{key}", response_model=SiteContentOut)
def get_content(key: str, db: Session = Depends(get_db)) -> SiteContentOut:
    """Public — returns the stored document for ``key`` (empty data if unset)."""
    row = _get_or_none(db, key)
    if not row:
        return SiteContentOut(key=key, data={}, updated_at=None)
    return SiteContentOut.model_validate(row)


@router.put(
    "/{key}",
    response_model=SiteContentOut,
    dependencies=[Depends(require_permission(MANAGE_SITE))],
)
def put_content(
    key: str,
    payload: SiteContentUpdate,
    db: Session = Depends(get_db),
) -> SiteContentOut:
    """Upsert the full content document for ``key`` (CEO / technical admin)."""
    if key not in ALLOWED_KEYS:
        # Be lenient but bounded — accept only known page keys.
        from app.core.exceptions import NotFoundError

        raise NotFoundError("Unknown site content key.")
    row = _get_or_none(db, key)
    if row:
        row.data = payload.data
    else:
        row = SiteContent(key=key, data=payload.data)
        db.add(row)
    db.commit()
    db.refresh(row)
    return SiteContentOut.model_validate(row)
