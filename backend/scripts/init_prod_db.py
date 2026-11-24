"""One-time production database bootstrap.

Creates every table and the single super-admin login — and nothing else
(no demo students/universities). Run this ONCE after pointing
``DATABASE_URL`` at your Supabase Postgres database:

    # PowerShell
    $env:DATABASE_URL = "postgresql+psycopg2://postgres:PASSWORD@HOST:5432/postgres"
    $env:SEED_SUPERADMIN_EMAIL = "you@example.com"
    $env:SEED_SUPERADMIN_PASSWORD = "a-strong-password"
    python scripts/init_prod_db.py

It is idempotent: re-running it will not duplicate the admin or drop data.
"""
from __future__ import annotations

import sys
from pathlib import Path

# Allow running as a plain script (`python scripts/init_prod_db.py`) by making
# the backend root importable.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.config import settings  # noqa: E402
from app.db.base import Base  # noqa: E402
from app.db.seed import _ensure_super_admin  # noqa: E402
from app.db.session import SessionLocal, engine  # noqa: E402

# Import the models package so every table is registered on Base.metadata
# before create_all runs.
import app.models  # noqa: E402,F401


def main() -> None:
    print(f"Connecting to: {engine.url.render_as_string(hide_password=True)}")
    print("Creating tables (idempotent)...")
    Base.metadata.create_all(engine)

    with SessionLocal() as db:
        admin = _ensure_super_admin(db)
        db.commit()
        print(f"Super-admin ready: {admin.email}")

    print("Done. Production database is ready.")


if __name__ == "__main__":
    main()
