"""Generate Postgres DDL for every model into supabase/schema_raw.sql.

Uses a SQLAlchemy "mock" engine so we get the exact CREATE TYPE / CREATE TABLE
/ CREATE INDEX statements for the Postgres dialect without needing a live DB.
The output is post-processed by build_schema_sql.py into the final, idempotent
supabase/schema.sql.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import create_mock_engine  # noqa: E402

import app.models  # noqa: E402,F401  (registers every table on Base.metadata)
from app.db.base import Base  # noqa: E402

_OUT = Path(__file__).resolve().parent.parent / "supabase" / "schema_raw.sql"
_lines: list[str] = []


def _dump(sql, *args, **kwargs):
    text = str(sql.compile(dialect=engine.dialect)).strip()
    if text:
        _lines.append(text + ";")


engine = create_mock_engine("postgresql+psycopg2://", _dump)
Base.metadata.create_all(engine, checkfirst=False)

_OUT.parent.mkdir(parents=True, exist_ok=True)
_OUT.write_text("\n\n".join(_lines) + "\n", encoding="utf-8")
print(f"Wrote {_OUT} ({len(_lines)} statements)")
