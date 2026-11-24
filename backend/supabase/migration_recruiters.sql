-- ============================================================================
-- RankAfrica — Recruiter approval migration
-- Run this WHOLE file in the Supabase SQL Editor. Safe to re-run.
-- Adds an approval state to user accounts. Existing accounts default to
-- APPROVED; new recruiter sign-ups start PENDING until an admin approves them.
-- ============================================================================

DO $$ BEGIN
  CREATE TYPE user_approval_status AS ENUM ('PENDING', 'APPROVED', 'REJECTED');
EXCEPTION WHEN duplicate_object THEN null;
END $$;

ALTER TABLE users
  ADD COLUMN IF NOT EXISTS approval_status user_approval_status NOT NULL DEFAULT 'APPROVED';
