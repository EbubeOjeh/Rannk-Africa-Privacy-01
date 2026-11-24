"""Seed the RankAfrica team (roles + staff accounts) into the live database.

Run ONCE after applying supabase/migration_team.sql, pointing DATABASE_URL at
your Supabase database:

    # PowerShell, from backend/
    $env:DATABASE_URL = "postgresql+psycopg2://...:6543/postgres"
    .venv\Scripts\python.exe scripts\seed_team.py

Idempotent: existing roles/accounts (matched by name/email) are left untouched.
Every seeded account uses the password 'rankpass' and must change it on first
login.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.db.session import SessionLocal, engine  # noqa: E402
from app.db.team_seed import EMPLOYEES_SEED, TEMP_PASSWORD, seed_team  # noqa: E402
import app.models  # noqa: E402,F401


def main() -> None:
    print(f"Connecting to: {engine.url.render_as_string(hide_password=True)}")
    with SessionLocal() as db:
        seed_team(db)
    print("Team seeded. Accounts (password: %s, must change on first login):" % TEMP_PASSWORD)
    for e in EMPLOYEES_SEED:
        print(f"  - {e['email']}  ({e['title']})")


if __name__ == "__main__":
    main()
