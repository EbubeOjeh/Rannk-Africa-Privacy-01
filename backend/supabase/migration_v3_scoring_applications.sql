-- RankAfrica — v3 per-field scoring + opportunity applications
-- ---------------------------------------------------------------------------
-- Run this WHOLE file ONCE in the Supabase SQL Editor on the PRODUCTION DB.
-- It is idempotent (safe to re-run): every statement uses IF NOT EXISTS or a
-- guarded enum block. Re-running the full schema.sql does NOT add the new
-- `students` columns (that table already exists), so this migration is required.
-- ---------------------------------------------------------------------------

-- 1) Student "Achievements & Profile Assessment" (/60 for non-Technology/Music
--    fields). profile_statement holds the free text; profile_score its AI score.
ALTER TABLE students ADD COLUMN IF NOT EXISTS profile_statement TEXT;
ALTER TABLE students ADD COLUMN IF NOT EXISTS profile_score FLOAT NOT NULL DEFAULT 0;

-- 2) Application status enum.
DO $$ BEGIN
  CREATE TYPE application_status AS ENUM ('RECEIVED', 'REVIEWED', 'SHORTLISTED', 'REJECTED', 'SELECTED');
EXCEPTION WHEN duplicate_object THEN null; END $$;

-- 3) Opportunity applications (students Apply → admins review applicants).
CREATE TABLE IF NOT EXISTS opportunity_applications (
	opportunity_id VARCHAR(36) NOT NULL,
	student_id VARCHAR(36) NOT NULL,
	status application_status NOT NULL DEFAULT 'RECEIVED',
	id VARCHAR(36) NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	PRIMARY KEY (id),
	CONSTRAINT uq_opportunity_application UNIQUE (opportunity_id, student_id),
	FOREIGN KEY(opportunity_id) REFERENCES opportunities (id) ON DELETE CASCADE,
	FOREIGN KEY(student_id) REFERENCES students (id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS ix_opportunity_applications_student_id ON opportunity_applications (student_id);
CREATE INDEX IF NOT EXISTS ix_opportunity_applications_opportunity_id ON opportunity_applications (opportunity_id);

-- Note: the legacy `transcripts` / `transcript_courses` tables and the
-- users.university_id / universities.approval_* columns are intentionally LEFT
-- IN PLACE (harmless dead columns) — dropping them is optional and not required.
