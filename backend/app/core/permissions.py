"""Permission catalog + resolver for the dynamic role system.

The app keeps its original coarse ``UserRole`` enum (SUPER_ADMIN, SCHOOL_ADMIN,
…) but layers a fine-grained permission set on top so company staff (role
``EMPLOYEE``) can be granted exactly the abilities an admin/CEO assigns them via
a custom :class:`~app.models.role.Role`.

Resolution rules:
* ``SUPER_ADMIN`` (the technical admin) and any role holding ``full_access``
  (the CEO) get **every** permission.
* ``SCHOOL_ADMIN`` / ``UNIVERSITY_ADMIN`` are retired legacy roles with no
  automatic grant (the platform is now fully student-driven).
* ``EMPLOYEE`` gets whatever their assigned company role lists.
"""
from __future__ import annotations

# --- Permission keys (the catalog the role editor exposes) -------------------
FULL_ACCESS = "full_access"
APPROVE_SCHOOLS = "approve_schools"
UPLOAD_TRANSCRIPTS = "upload_transcripts"
MANAGE_STUDENTS = "manage_students"
APPROVE_STUDENTS = "approve_students"
MANAGE_CYCLES = "manage_cycles"
VIEW_ANALYTICS = "view_analytics"
MANAGE_TEAM = "manage_team"
APPROVE_RECRUITERS = "approve_recruiters"
MANAGE_SITE = "manage_site"

# Ordered catalog with human labels — returned to the role editor UI.
PERMISSION_CATALOG: list[dict[str, str]] = [
    {"key": FULL_ACCESS, "label": "Full access", "description": "Everything an admin can do (CEO level)."},
    {"key": APPROVE_RECRUITERS, "label": "Approve recruiters", "description": "Review and approve/reject recruiter & employer accounts."},
    {"key": APPROVE_STUDENTS, "label": "Approve students", "description": "Approve students onto the public leaderboard."},
    {"key": MANAGE_CYCLES, "label": "Manage cycles", "description": "Open, publish and close submission cycles."},
    {"key": VIEW_ANALYTICS, "label": "View analytics", "description": "See platform analytics dashboards."},
    {"key": MANAGE_TEAM, "label": "Manage team & roles", "description": "Create/block/delete team members and edit roles."},
    {"key": MANAGE_SITE, "label": "Manage website content", "description": "Edit the public landing page — text, cards, icons and colours — from the dashboard."},
]

ALL_PERMISSIONS: frozenset[str] = frozenset(p["key"] for p in PERMISSION_CATALOG)


def get_permissions(user) -> frozenset[str]:
    """Resolve the effective permission set for a user object.

    RankAfrica is now fully student-driven — the legacy SCHOOL_ADMIN /
    UNIVERSITY_ADMIN roles no longer receive any automatic grant, so an old
    school-admin account is inert until an admin assigns it a company role.
    """
    # Imported lazily to avoid a model import cycle.
    from app.models.user import UserRole

    if user.role == UserRole.SUPER_ADMIN:
        return ALL_PERMISSIONS

    company_role = getattr(user, "company_role", None)
    role_perms = set(company_role.permissions or []) if company_role else set()
    if FULL_ACCESS in role_perms:
        return ALL_PERMISSIONS

    return frozenset(set(role_perms) & set(ALL_PERMISSIONS))


def has_permission(user, key: str) -> bool:
    return key in get_permissions(user)
