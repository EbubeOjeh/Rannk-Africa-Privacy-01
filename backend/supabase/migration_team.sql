-- ============================================================================
-- RankAfrica — Team & Roles migration (STEP 1 of 2)
-- Run this WHOLE file in the Supabase SQL Editor, then run migration_team_seed.sql.
-- It only changes the schema (adds the employee role value, the new user
-- columns, and the roles table) + seeds the default company roles.
-- Safe to re-run.
-- ============================================================================

-- 1. New coarse role value for company staff.
ALTER TYPE user_role ADD VALUE IF NOT EXISTS 'EMPLOYEE';

-- 2. New columns on users (profile + forced password change + company role link).
ALTER TABLE users ADD COLUMN IF NOT EXISTS must_change_password BOOLEAN NOT NULL DEFAULT false;
ALTER TABLE users ADD COLUMN IF NOT EXISTS avatar_url VARCHAR(500);
ALTER TABLE users ADD COLUMN IF NOT EXISTS title VARCHAR(120);
ALTER TABLE users ADD COLUMN IF NOT EXISTS company_role_id VARCHAR(36);

-- 3. The dynamic-role table.
CREATE TABLE IF NOT EXISTS roles (
  name        VARCHAR(80) NOT NULL,
  description VARCHAR(300),
  permissions JSON NOT NULL,
  is_system   BOOLEAN NOT NULL,
  id          VARCHAR(36) NOT NULL,
  created_at  TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
  updated_at  TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
  PRIMARY KEY (id)
);
CREATE UNIQUE INDEX IF NOT EXISTS ix_roles_name ON roles (name);

-- 4. Link users.company_role_id -> roles.id (idempotent).
DO $$ BEGIN
  ALTER TABLE users
    ADD CONSTRAINT users_company_role_id_fkey
    FOREIGN KEY (company_role_id) REFERENCES roles (id) ON DELETE SET NULL;
EXCEPTION WHEN duplicate_object THEN null;
END $$;

-- 5. Seed the default company roles (titles + permissions).
INSERT INTO roles (id, name, description, permissions, is_system) VALUES
  (gen_random_uuid()::text, 'CEO', 'Chief Executive Officer — full platform access.', '["full_access"]'::json, true),
  (gen_random_uuid()::text, 'COO', 'Chief Operating Officer.', '["approve_schools", "upload_transcripts"]'::json, true),
  (gen_random_uuid()::text, 'CMO', 'Chief Marketing Officer.', '["approve_schools", "upload_transcripts"]'::json, true),
  (gen_random_uuid()::text, 'Chief Partnerships Officer', 'University, corporate, government & NGO partnerships.', '["approve_schools", "upload_transcripts"]'::json, true),
  (gen_random_uuid()::text, 'Chief Programs Officer', 'Internship programs, student engagement & impact.', '["approve_schools", "upload_transcripts"]'::json, true)
ON CONFLICT (name) DO NOTHING;
