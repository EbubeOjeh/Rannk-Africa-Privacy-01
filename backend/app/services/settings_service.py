"""Global platform settings backed by the site_content CMS.

The "rankings release" switch lets an admin keep all public rankings hidden while
registration is open, then reveal them once registration closes — so nobody can
game the leaderboard by watching interim results. It is stored as a site_content
document under the ``rankings`` key (public read, ``manage_site`` write), so it
needs no schema change and can be toggled from the admin dashboard.
"""
from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.site_content import SiteContent

RANKINGS_KEY = "rankings"

DEFAULT_RELEASE_MESSAGE = (
    "Rankings will be released after the registration period closes. Follow our "
    "social media channels to be notified as soon as they are published."
)


def get_rankings_release(db: Session) -> dict:
    """Return {released, message}. Defaults to NOT released (hidden) when unset."""
    row = db.query(SiteContent).filter(SiteContent.key == RANKINGS_KEY).first()
    data = row.data if (row and isinstance(row.data, dict)) else {}
    return {
        "released": bool(data.get("released", False)),
        "message": data.get("message") or DEFAULT_RELEASE_MESSAGE,
    }


def is_rankings_released(db: Session) -> bool:
    return get_rankings_release(db)["released"]
