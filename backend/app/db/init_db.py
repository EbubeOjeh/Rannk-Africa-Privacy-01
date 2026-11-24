"""Idempotent DB bootstrap.

On startup we:
  1. Run ``Base.metadata.create_all`` so any *new* tables get created
     (existing tables are untouched — this is idempotent).
  2. Backfill missing columns on existing tables for the SQLite dev path.
  3. If the DB has zero universities AND ``AUTO_SEED=true``, seed the demo data.

In production set ``AUTO_SEED=false`` and run Alembic + a controlled seed
script instead.

NOTE: if you're upgrading an old SQLite dev database, the safest thing is
to delete ``rankafrica.db`` and let this file re-create it from scratch with
the new schema + seed data. The backfill below covers the most common added
columns but won't recover from arbitrary schema drift.
"""
from __future__ import annotations

from sqlalchemy import inspect, select, text

from app.core.config import settings
from app.core.logging import logger
from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.models.university import University


# Lightweight, dev-only column backfill for SQLite. In production this is
# handled by Alembic — keep the dict accurate so dev DBs survive minor
# schema changes without a hard reset.
_SQLITE_COLUMN_BACKFILL: dict[str, dict[str, str]] = {
    "students": {
        "phone_number": "VARCHAR(40)",
        "linkedin_url": "VARCHAR(500)",
        "academic_score": "FLOAT NOT NULL DEFAULT 0",
        "project_score": "FLOAT NOT NULL DEFAULT 0",
        "achievement_score": "FLOAT NOT NULL DEFAULT 0",
        "profile_score": "FLOAT NOT NULL DEFAULT 0",
        "profile_statement": "TEXT",
        "research_score": "FLOAT NOT NULL DEFAULT 0",
        "leadership_score": "FLOAT NOT NULL DEFAULT 0",
        "experience_score": "FLOAT NOT NULL DEFAULT 0",
        "competition_score": "FLOAT NOT NULL DEFAULT 0",
        "final_score": "FLOAT NOT NULL DEFAULT 0",
        "normalized_cgpa": "FLOAT",
        "standardized_gpa_4": "FLOAT",
        "class_of_degree": "VARCHAR(40)",
        "submission_cycle_id": "VARCHAR(36)",
        "approval_status": "VARCHAR(20) NOT NULL DEFAULT 'pending'",
        "is_publicly_visible": "BOOLEAN NOT NULL DEFAULT 0",
        "approval_notes": "VARCHAR(500)",
        "approved_at": "DATETIME",
        "approved_by_id": "VARCHAR(36)",
        # PRS v2.0 — student self-service profile fields.
        "year_of_study": "INTEGER",
        "course": "VARCHAR(200)",
        "faculty": "VARCHAR(200)",
        "skills": "JSON",
        "languages": "JSON",
        "resume_url": "VARCHAR(500)",
        "transcript_url": "VARCHAR(500)",
        "portfolio_url": "VARCHAR(500)",
        "github_url": "VARCHAR(500)",
        "behance_url": "VARCHAR(500)",
        "google_scholar_url": "VARCHAR(500)",
        "music_url": "VARCHAR(500)",
        "whatsapp_number": "VARCHAR(40)",
        "user_id": "VARCHAR(36)",
        "is_self_registered": "BOOLEAN NOT NULL DEFAULT 0",
        "terms_accepted_at": "DATETIME",
    },
    "universities": {
        "state": "VARCHAR(80)",
        "accreditation_type": "VARCHAR(80)",
        "institution_type": "VARCHAR(20) NOT NULL DEFAULT 'university'",
        "domain": "VARCHAR(120)",
        "approval_status": "VARCHAR(20) NOT NULL DEFAULT 'approved'",
        "approval_notes": "VARCHAR(500)",
        "approved_at": "DATETIME",
        "approved_by_id": "VARCHAR(36)",
    },
    "users": {
        "organization": "VARCHAR(200)",
        "suspension_reason": "VARCHAR(500)",
        "suspended_at": "DATETIME",
    },
    "evaluation_results": {
        "academic_score": "FLOAT NOT NULL DEFAULT 0",
        "project_score": "FLOAT NOT NULL DEFAULT 0",
        "achievement_score": "FLOAT NOT NULL DEFAULT 0",
        "final_score": "FLOAT NOT NULL DEFAULT 0",
    },
}


def _backfill_sqlite_columns() -> None:
    if not engine.url.get_backend_name().startswith("sqlite"):
        return
    inspector = inspect(engine)
    with engine.begin() as conn:
        for table, columns in _SQLITE_COLUMN_BACKFILL.items():
            if not inspector.has_table(table):
                continue
            existing = {c["name"] for c in inspector.get_columns(table)}
            for col_name, col_type in columns.items():
                if col_name in existing:
                    continue
                logger.info(f"Adding missing column {table}.{col_name} ({col_type}).")
                conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {col_name} {col_type}"))


def init_db() -> None:
    # create_all is idempotent — only creates tables that don't exist yet.
    Base.metadata.create_all(engine)
    _backfill_sqlite_columns()

    if not settings.AUTO_SEED:
        return

    with SessionLocal() as db:
        any_uni = db.execute(select(University).limit(1)).first()
        if any_uni:
            return
        logger.info("Database is empty + AUTO_SEED=true -> seeding demo data.")
        from app.db.privacy_seed import run as run_seed  # local import to avoid circular

        run_seed()
