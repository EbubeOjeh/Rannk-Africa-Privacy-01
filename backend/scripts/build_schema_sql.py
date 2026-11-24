"""Turn schema_raw.sql into the final, idempotent supabase/schema.sql.

- Wraps every `CREATE TYPE ... AS ENUM` in a DO block (Postgres enums have no
  IF NOT EXISTS), so the file is safe to re-run.
- Adds `IF NOT EXISTS` to CREATE TABLE / CREATE INDEX.
- Appends a seed INSERT for the super-admin (bcrypt-hashed here), matching the
  "paste this whole file into the Supabase SQL Editor" flow.
"""
from __future__ import annotations

import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import json as _json  # noqa: E402

from app.core.security import hash_password  # noqa: E402
from app.db.team_seed import CTO_NAME, CTO_ROLE, EMPLOYEES_SEED, ROLES_SEED, TEMP_PASSWORD  # noqa: E402

HERE = Path(__file__).resolve().parent.parent
RAW = HERE / "supabase" / "schema_raw.sql"
OUT = HERE / "supabase" / "schema.sql"

ADMIN_ID = "00000000-0000-0000-0000-000000000001"
ADMIN_EMAIL = os.environ.get("SEED_SUPERADMIN_EMAIL", "admin@rankafrica.org").lower()
ADMIN_PASSWORD = os.environ.get("SEED_SUPERADMIN_PASSWORD", "ChangeMe123!")
ADMIN_NAME = "Super Admin"

HEADER = """\
-- ============================================================================
-- RankAfrica — Supabase schema
-- Run this WHOLE file in the Supabase SQL Editor (Dashboard -> SQL -> New query).
-- It is safe to re-run: enum types are guarded, and tables/indexes use
-- IF NOT EXISTS. It creates every table the backend expects, plus one
-- super-admin login so you can sign in immediately.
--
-- Default super-admin (CHANGE THE PASSWORD after first login):
--   email:    {email}
--   password: {password}
-- ============================================================================
""".format(email=ADMIN_EMAIL, password=ADMIN_PASSWORD)

SEED = """\

-- ---------------------------------------------------------------------------
-- SEED: super-admin login (no demo data). Password is bcrypt-hashed.
-- Re-running does nothing if the email already exists.
-- ---------------------------------------------------------------------------
INSERT INTO users (id, name, email, password_hash, role, is_active, is_email_verified, must_change_password)
VALUES (
  '{id}',
  '{name}',
  '{email}',
  '{pwhash}',
  'SUPER_ADMIN',
  true,
  true,
  false
)
ON CONFLICT (email) DO NOTHING;
"""


def transform(statement: str) -> str:
    # `statement` has no trailing ';' (it was the split delimiter); we re-add it.
    s = statement.strip()
    if s.upper().startswith("CREATE TYPE"):
        return (
            "DO $$ BEGIN\n"
            f"  {s};\n"
            "EXCEPTION WHEN duplicate_object THEN null;\n"
            "END $$;"
        )
    if s.upper().startswith("CREATE TABLE "):
        s = re.sub(r"^CREATE TABLE ", "CREATE TABLE IF NOT EXISTS ", s, count=1, flags=re.I)
    elif s.upper().startswith("CREATE UNIQUE INDEX "):
        s = re.sub(r"^CREATE UNIQUE INDEX ", "CREATE UNIQUE INDEX IF NOT EXISTS ", s, count=1, flags=re.I)
    elif s.upper().startswith("CREATE INDEX "):
        s = re.sub(r"^CREATE INDEX ", "CREATE INDEX IF NOT EXISTS ", s, count=1, flags=re.I)
    return s + ";"


def _sql_str(value: str) -> str:
    return value.replace("'", "''")


def build_team_seed() -> str:
    """SQL that seeds the default company roles + staff accounts.

    Safe inside schema.sql because the enum is CREATEd (not ALTERed) here, so
    the new 'employee' value is usable in the same run.
    """
    team_pwhash = hash_password(TEMP_PASSWORD).replace("'", "''")
    role_rows = ",\n  ".join(
        "(gen_random_uuid()::text, '{name}', '{desc}', '{perms}'::json, true)".format(
            name=_sql_str(r["name"]),
            desc=_sql_str(r["description"]),
            perms=_json.dumps(r["permissions"]).replace("'", "''"),
        )
        for r in ROLES_SEED
    )
    emp_rows = ",\n  ".join(
        "(gen_random_uuid()::text, '{name}', '{email}', '{pw}', '{role}', true, true, true, '{title}', "
        "(SELECT id FROM roles WHERE name = '{crole}'))".format(
            name=_sql_str(e["name"]),
            email=_sql_str(e["email"]),
            pw=team_pwhash,
            role=e["user_role"],
            title=_sql_str(e["title"]),
            crole=_sql_str(e["company_role"]),
        )
        for e in EMPLOYEES_SEED
    )
    return (
        "\n-- ---------------------------------------------------------------------------\n"
        "-- SEED: company roles + staff accounts (password 'rankpass', must change on\n"
        "-- first login). Re-running is a no-op (ON CONFLICT).\n"
        "-- ---------------------------------------------------------------------------\n"
        "INSERT INTO roles (id, name, description, permissions, is_system) VALUES\n"
        f"  {role_rows}\n"
        "ON CONFLICT (name) DO NOTHING;\n\n"
        "INSERT INTO users (id, name, email, password_hash, role, is_active, is_email_verified, must_change_password, title, company_role_id) VALUES\n"
        f"  {emp_rows}\n"
        "ON CONFLICT (email) DO NOTHING;\n\n"
        "-- The technical admin also represents the CTO on the public team page.\n"
        f"UPDATE users SET name = '{_sql_str(CTO_NAME)}', title = '{_sql_str(CTO_ROLE)}', "
        f"company_role_id = (SELECT id FROM roles WHERE name = '{_sql_str(CTO_ROLE)}') "
        f"WHERE email = '{_sql_str(ADMIN_EMAIL)}' AND company_role_id IS NULL;\n"
    )


def main() -> None:
    raw = RAW.read_text(encoding="utf-8")
    statements = [chunk for chunk in raw.split(";\n") if chunk.strip()]
    transformed = [transform(st) for st in statements]

    pwhash = hash_password(ADMIN_PASSWORD).replace("'", "''")
    seed = SEED.format(id=ADMIN_ID, name=ADMIN_NAME, email=ADMIN_EMAIL, pwhash=pwhash)

    OUT.write_text(
        HEADER + "\n" + "\n\n".join(transformed) + "\n" + seed + build_team_seed(),
        encoding="utf-8",
    )
    print(f"Wrote {OUT}")
    print(f"Admin seeded: {ADMIN_EMAIL} / {ADMIN_PASSWORD}")
    print(f"Team seeded: {len(EMPLOYEES_SEED)} staff + {len(ROLES_SEED)} roles")


if __name__ == "__main__":
    main()
