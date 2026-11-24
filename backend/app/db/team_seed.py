"""Canonical RankAfrica team & role seed data.

Used by ``scripts/seed_team.py`` (live DB) and by ``scripts/build_schema_sql.py``
(to embed the same roster into the fresh-install schema.sql). Keep the roster
here so the two never drift.
"""
from __future__ import annotations

TEMP_PASSWORD = "rankpass"

# The technical admin account also represents the CTO on the public team page.
CTO_ROLE = "Chief Technology Officer"
CTO_NAME = "Offia Victory"

# Default company roles (full titles). Permissions are keys from app.core.permissions.
ROLES_SEED: list[dict] = [
    {"name": "Chief Executive Officer", "description": "Overall leadership, vision, partnerships and major decisions.", "permissions": ["full_access"]},
    {"name": CTO_ROLE, "description": "Technology, engineering and platform direction.", "permissions": ["full_access"]},
    {"name": "Chief Operating Officer", "description": "Operations, project management, team coordination and execution.", "permissions": ["view_analytics", "manage_cycles", "approve_students"]},
    {"name": "Chief Marketing Officer", "description": "Marketing, branding, social media, PR and growth.", "permissions": ["manage_site", "view_analytics"]},
    {"name": "Chief Partnerships Officer", "description": "University, corporate, government and NGO partnerships.", "permissions": ["approve_recruiters", "view_analytics"]},
    {"name": "Chief Programs Officer", "description": "Internship programs, student engagement and impact measurement.", "permissions": ["approve_students", "view_analytics"]},
]

# Seeded staff accounts. ``user_role`` is the coarse enum; ``company_role`` is
# the dynamic role granting permissions. Everyone starts with must_change_password.
EMPLOYEES_SEED: list[dict] = [
    {"name": "Kennedy", "email": "kennedy@rankafrica.org", "user_role": "SUPER_ADMIN", "company_role": "Chief Executive Officer", "title": "Chief Executive Officer"},
    {"name": "Austin", "email": "austin@rankafrica.org", "user_role": "EMPLOYEE", "company_role": "Chief Operating Officer", "title": "Chief Operating Officer"},
    {"name": "Ike", "email": "ike@rankafrica.org", "user_role": "EMPLOYEE", "company_role": "Chief Marketing Officer", "title": "Chief Marketing Officer"},
    {"name": "Josh", "email": "josh@rankafrica.org", "user_role": "EMPLOYEE", "company_role": "Chief Partnerships Officer", "title": "Chief Partnerships Officer"},
    {"name": "Benjamin", "email": "benjamin@rankafrica.org", "user_role": "EMPLOYEE", "company_role": "Chief Programs Officer", "title": "Chief Programs Officer"},
]


def seed_team(db, *, password: str = TEMP_PASSWORD) -> None:
    """Idempotently create the default roles and staff accounts."""
    from app.core.security import hash_password
    from app.models.role import Role
    from app.models.user import User, UserRole

    role_by_name: dict[str, Role] = {}
    for spec in ROLES_SEED:
        role = db.query(Role).filter(Role.name == spec["name"]).first()
        if not role:
            role = Role(
                name=spec["name"],
                description=spec["description"],
                permissions=list(spec["permissions"]),
                is_system=True,
            )
            db.add(role)
            db.flush()
        role_by_name[spec["name"]] = role

    for spec in EMPLOYEES_SEED:
        if db.query(User).filter(User.email == spec["email"]).first():
            continue
        company_role = role_by_name.get(spec["company_role"])
        db.add(
            User(
                name=spec["name"],
                email=spec["email"],
                password_hash=hash_password(password),
                role=UserRole[spec["user_role"]],
                company_role_id=company_role.id if company_role else None,
                title=spec["title"],
                is_active=True,
                is_email_verified=True,
                must_change_password=True,
            )
        )

    # The technical super-admin doubles as the CTO so the team page is complete.
    from app.core.config import settings

    cto_role = role_by_name.get(CTO_ROLE)
    admin = db.query(User).filter(User.email == settings.SEED_SUPERADMIN_EMAIL.lower()).first()
    if admin and cto_role and not admin.company_role_id:
        admin.company_role_id = cto_role.id
        admin.title = CTO_ROLE
        if admin.name in (None, "", "Super Admin"):
            admin.name = CTO_NAME
    db.commit()
