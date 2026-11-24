-- ============================================================================
-- RankAfrica — PRS v2.0 migration (apply ONCE to the existing prod Supabase DB)
-- Idempotent: safe to re-run. Paste the WHOLE file into the Supabase SQL editor.
-- If the editor errors on an ALTER TYPE line, run the 6 ALTER TYPE lines first
-- on their own, then run the rest.
-- ============================================================================

-- 1) New values on the existing achievement_type enum (uppercase = enum NAMES)
ALTER TYPE achievement_type ADD VALUE IF NOT EXISTS 'AWARD';
ALTER TYPE achievement_type ADD VALUE IF NOT EXISTS 'CERTIFICATION';
ALTER TYPE achievement_type ADD VALUE IF NOT EXISTS 'SCHOLARSHIP';
ALTER TYPE achievement_type ADD VALUE IF NOT EXISTS 'GRANT';
ALTER TYPE achievement_type ADD VALUE IF NOT EXISTS 'FELLOWSHIP';
ALTER TYPE achievement_type ADD VALUE IF NOT EXISTS 'NATIONAL_RECOGNITION';

-- 2) New enum types (guarded — no-op if they already exist)
DO $$ BEGIN
  CREATE TYPE research_type AS ENUM ('JOURNAL_PUBLICATION', 'CONFERENCE_PAPER', 'UNDERGRADUATE_RESEARCH', 'RESEARCH_ASSISTANTSHIP', 'BOOK_CHAPTER');
EXCEPTION WHEN duplicate_object THEN null;
END $$;
DO $$ BEGIN
  CREATE TYPE experience_type AS ENUM ('INTERNSHIP', 'VOLUNTEER', 'STARTUP', 'BUSINESS', 'EMPLOYMENT');
EXCEPTION WHEN duplicate_object THEN null;
END $$;
DO $$ BEGIN
  CREATE TYPE competition_type AS ENUM ('HACKATHON', 'MOOT_COURT', 'BUSINESS_COMPETITION', 'DEBATE', 'MUSIC_AWARD', 'INNOVATION_CHALLENGE');
EXCEPTION WHEN duplicate_object THEN null;
END $$;
DO $$ BEGIN
  CREATE TYPE competition_result AS ENUM ('WINNER', 'RUNNER_UP', 'FINALIST', 'PARTICIPANT');
EXCEPTION WHEN duplicate_object THEN null;
END $$;
DO $$ BEGIN
  CREATE TYPE leadership_type AS ENUM ('STUDENT_LEADERSHIP', 'VOLUNTEER_WORK', 'COMMUNITY_IMPACT', 'PROFESSIONAL_ORG');
EXCEPTION WHEN duplicate_object THEN null;
END $$;
DO $$ BEGIN
  CREATE TYPE opportunity_type AS ENUM ('INTERNSHIP', 'GRADUATE_JOB', 'SCHOLARSHIP', 'RESEARCH', 'COMPETITION', 'LEADERSHIP_PROGRAM');
EXCEPTION WHEN duplicate_object THEN null;
END $$;
DO $$ BEGIN
  CREATE TYPE ai_flag_type AS ENUM ('FAKE_TRANSCRIPT', 'EDITED_CERTIFICATE', 'DUPLICATE_PUBLICATION', 'PLAGIARIZED_PROJECT', 'SUSPICIOUS_CLAIM', 'DUPLICATE_ACCOUNT');
EXCEPTION WHEN duplicate_object THEN null;
END $$;
DO $$ BEGIN
  CREATE TYPE ai_flag_severity AS ENUM ('LOW', 'MEDIUM', 'HIGH');
EXCEPTION WHEN duplicate_object THEN null;
END $$;
DO $$ BEGIN
  CREATE TYPE ai_flag_status AS ENUM ('OPEN', 'CONFIRMED', 'DISMISSED');
EXCEPTION WHEN duplicate_object THEN null;
END $$;

-- 3) New columns on existing tables
ALTER TABLE students ADD COLUMN IF NOT EXISTS year_of_study INTEGER;
ALTER TABLE students ADD COLUMN IF NOT EXISTS course VARCHAR(200);
ALTER TABLE students ADD COLUMN IF NOT EXISTS faculty VARCHAR(200);
ALTER TABLE students ADD COLUMN IF NOT EXISTS skills JSON;
ALTER TABLE students ADD COLUMN IF NOT EXISTS languages JSON;
ALTER TABLE students ADD COLUMN IF NOT EXISTS resume_url VARCHAR(500);
ALTER TABLE students ADD COLUMN IF NOT EXISTS portfolio_url VARCHAR(500);
ALTER TABLE students ADD COLUMN IF NOT EXISTS github_url VARCHAR(500);
ALTER TABLE students ADD COLUMN IF NOT EXISTS behance_url VARCHAR(500);
ALTER TABLE students ADD COLUMN IF NOT EXISTS google_scholar_url VARCHAR(500);
ALTER TABLE students ADD COLUMN IF NOT EXISTS music_url VARCHAR(500);
ALTER TABLE students ADD COLUMN IF NOT EXISTS whatsapp_number VARCHAR(40);
ALTER TABLE students ADD COLUMN IF NOT EXISTS user_id VARCHAR(36);
ALTER TABLE students ADD COLUMN IF NOT EXISTS is_self_registered BOOLEAN NOT NULL DEFAULT false;
ALTER TABLE students ADD COLUMN IF NOT EXISTS terms_accepted_at TIMESTAMPTZ;
ALTER TABLE students ADD COLUMN IF NOT EXISTS research_score DOUBLE PRECISION NOT NULL DEFAULT 0;
ALTER TABLE students ADD COLUMN IF NOT EXISTS leadership_score DOUBLE PRECISION NOT NULL DEFAULT 0;
ALTER TABLE students ADD COLUMN IF NOT EXISTS experience_score DOUBLE PRECISION NOT NULL DEFAULT 0;
ALTER TABLE students ADD COLUMN IF NOT EXISTS competition_score DOUBLE PRECISION NOT NULL DEFAULT 0;
ALTER TABLE users ADD COLUMN IF NOT EXISTS suspension_reason VARCHAR(500);
ALTER TABLE users ADD COLUMN IF NOT EXISTS suspended_at TIMESTAMPTZ;

-- 4) Allow multiple projects per student (drop the old 1:1 unique constraint,
--    whatever it was named).
DO $$
DECLARE cname text;
BEGIN
  SELECT conname INTO cname
  FROM pg_constraint
  WHERE conrelid = 'project_submissions'::regclass
    AND contype = 'u'
    AND conkey = ARRAY[(
      SELECT attnum FROM pg_attribute
      WHERE attrelid = 'project_submissions'::regclass AND attname = 'student_id'
    )];
  IF cname IS NOT NULL THEN
    EXECUTE 'ALTER TABLE project_submissions DROP CONSTRAINT ' || quote_ident(cname);
  END IF;
END $$;
DROP INDEX IF EXISTS project_submissions_student_id_key;

-- 5) New tables + indexes
CREATE TABLE IF NOT EXISTS research_publications (
	student_id VARCHAR(36) NOT NULL, 
	type research_type NOT NULL, 
	title VARCHAR(300) NOT NULL, 
	venue VARCHAR(240), 
	year INTEGER, 
	citations INTEGER NOT NULL, 
	doi VARCHAR(200), 
	link VARCHAR(500), 
	description TEXT, 
	evidence_url VARCHAR(500), 
	ai_quality FLOAT, 
	verification_status verification_status NOT NULL, 
	verified_at TIMESTAMP WITH TIME ZONE, 
	verified_by_id VARCHAR(36), 
	rejection_reason TEXT, 
	id VARCHAR(36) NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(student_id) REFERENCES students (id) ON DELETE CASCADE, 
	FOREIGN KEY(verified_by_id) REFERENCES users (id) ON DELETE SET NULL
);
CREATE INDEX IF NOT EXISTS ix_research_publications_type ON research_publications (type);
CREATE INDEX IF NOT EXISTS ix_research_publications_student_id ON research_publications (student_id);
CREATE TABLE IF NOT EXISTS experiences (
	student_id VARCHAR(36) NOT NULL, 
	type experience_type NOT NULL, 
	organization VARCHAR(200) NOT NULL, 
	role_title VARCHAR(200), 
	location VARCHAR(160), 
	start_date VARCHAR(40), 
	end_date VARCHAR(40), 
	is_current BOOLEAN NOT NULL, 
	duration_months INTEGER, 
	description TEXT, 
	link VARCHAR(500), 
	evidence_url VARCHAR(500), 
	verification_status verification_status NOT NULL, 
	verified_at TIMESTAMP WITH TIME ZONE, 
	verified_by_id VARCHAR(36), 
	rejection_reason TEXT, 
	id VARCHAR(36) NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(student_id) REFERENCES students (id) ON DELETE CASCADE, 
	FOREIGN KEY(verified_by_id) REFERENCES users (id) ON DELETE SET NULL
);
CREATE INDEX IF NOT EXISTS ix_experiences_type ON experiences (type);
CREATE INDEX IF NOT EXISTS ix_experiences_student_id ON experiences (student_id);
CREATE TABLE IF NOT EXISTS competitions (
	student_id VARCHAR(36) NOT NULL, 
	type competition_type NOT NULL, 
	result competition_result NOT NULL, 
	title VARCHAR(240) NOT NULL, 
	organizer VARCHAR(200), 
	year INTEGER, 
	description TEXT, 
	link VARCHAR(500), 
	evidence_url VARCHAR(500), 
	verification_status verification_status NOT NULL, 
	verified_at TIMESTAMP WITH TIME ZONE, 
	verified_by_id VARCHAR(36), 
	rejection_reason TEXT, 
	id VARCHAR(36) NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(student_id) REFERENCES students (id) ON DELETE CASCADE, 
	FOREIGN KEY(verified_by_id) REFERENCES users (id) ON DELETE SET NULL
);
CREATE INDEX IF NOT EXISTS ix_competitions_student_id ON competitions (student_id);
CREATE INDEX IF NOT EXISTS ix_competitions_type ON competitions (type);
CREATE TABLE IF NOT EXISTS leadership_activities (
	student_id VARCHAR(36) NOT NULL, 
	type leadership_type NOT NULL, 
	title VARCHAR(240) NOT NULL, 
	organization VARCHAR(200), 
	role_title VARCHAR(200), 
	start_date VARCHAR(40), 
	end_date VARCHAR(40), 
	description TEXT, 
	link VARCHAR(500), 
	evidence_url VARCHAR(500), 
	verification_status verification_status NOT NULL, 
	verified_at TIMESTAMP WITH TIME ZONE, 
	verified_by_id VARCHAR(36), 
	rejection_reason TEXT, 
	id VARCHAR(36) NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(student_id) REFERENCES students (id) ON DELETE CASCADE, 
	FOREIGN KEY(verified_by_id) REFERENCES users (id) ON DELETE SET NULL
);
CREATE INDEX IF NOT EXISTS ix_leadership_activities_type ON leadership_activities (type);
CREATE INDEX IF NOT EXISTS ix_leadership_activities_student_id ON leadership_activities (student_id);
CREATE TABLE IF NOT EXISTS opportunities (
	posted_by_id VARCHAR(36), 
	organization VARCHAR(200), 
	type opportunity_type NOT NULL, 
	title VARCHAR(240) NOT NULL, 
	description TEXT NOT NULL, 
	location VARCHAR(160), 
	requirements TEXT, 
	apply_url VARCHAR(500), 
	deadline VARCHAR(40), 
	field_id VARCHAR(36), 
	min_gpa FLOAT, 
	min_score FLOAT, 
	graduation_year INTEGER, 
	is_active BOOLEAN NOT NULL, 
	is_featured BOOLEAN NOT NULL, 
	closed_at TIMESTAMP WITH TIME ZONE, 
	id VARCHAR(36) NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(posted_by_id) REFERENCES users (id) ON DELETE SET NULL, 
	FOREIGN KEY(field_id) REFERENCES fields (id) ON DELETE SET NULL
);
CREATE INDEX IF NOT EXISTS ix_opportunities_is_active ON opportunities (is_active);
CREATE INDEX IF NOT EXISTS ix_opportunities_type ON opportunities (type);
CREATE INDEX IF NOT EXISTS ix_opportunities_field_id ON opportunities (field_id);
CREATE INDEX IF NOT EXISTS ix_opportunities_posted_by_id ON opportunities (posted_by_id);
CREATE TABLE IF NOT EXISTS saved_candidates (
	employer_id VARCHAR(36) NOT NULL, 
	student_id VARCHAR(36) NOT NULL, 
	notes TEXT, 
	id VARCHAR(36) NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT uq_saved_candidate UNIQUE (employer_id, student_id), 
	FOREIGN KEY(employer_id) REFERENCES users (id) ON DELETE CASCADE, 
	FOREIGN KEY(student_id) REFERENCES students (id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS ix_saved_candidates_employer_id ON saved_candidates (employer_id);
CREATE INDEX IF NOT EXISTS ix_saved_candidates_student_id ON saved_candidates (student_id);
CREATE TABLE IF NOT EXISTS student_badges (
	student_id VARCHAR(36) NOT NULL, 
	badge_key VARCHAR(60) NOT NULL, 
	is_auto BOOLEAN NOT NULL, 
	awarded_by_id VARCHAR(36), 
	id VARCHAR(36) NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT uq_student_badge UNIQUE (student_id, badge_key), 
	FOREIGN KEY(student_id) REFERENCES students (id) ON DELETE CASCADE, 
	FOREIGN KEY(awarded_by_id) REFERENCES users (id) ON DELETE SET NULL
);
CREATE INDEX IF NOT EXISTS ix_student_badges_student_id ON student_badges (student_id);
CREATE INDEX IF NOT EXISTS ix_student_badges_badge_key ON student_badges (badge_key);
CREATE TABLE IF NOT EXISTS terms_acceptances (
	user_id VARCHAR(36), 
	student_id VARCHAR(36), 
	version VARCHAR(20) NOT NULL, 
	ip_address VARCHAR(60), 
	user_agent TEXT, 
	accepted_text TEXT, 
	id VARCHAR(36) NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE SET NULL, 
	FOREIGN KEY(student_id) REFERENCES students (id) ON DELETE SET NULL
);
CREATE INDEX IF NOT EXISTS ix_terms_acceptances_user_id ON terms_acceptances (user_id);
CREATE INDEX IF NOT EXISTS ix_terms_acceptances_student_id ON terms_acceptances (student_id);
CREATE TABLE IF NOT EXISTS ai_flags (
	student_id VARCHAR(36), 
	entity_type VARCHAR(40), 
	entity_id VARCHAR(36), 
	flag_type ai_flag_type NOT NULL, 
	severity ai_flag_severity NOT NULL, 
	status ai_flag_status NOT NULL, 
	reason TEXT NOT NULL, 
	details JSON, 
	ai_engine VARCHAR(60), 
	reviewed_by_id VARCHAR(36), 
	reviewed_at TIMESTAMP WITH TIME ZONE, 
	review_notes TEXT, 
	id VARCHAR(36) NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(student_id) REFERENCES students (id) ON DELETE CASCADE, 
	FOREIGN KEY(reviewed_by_id) REFERENCES users (id) ON DELETE SET NULL
);
CREATE INDEX IF NOT EXISTS ix_ai_flags_status ON ai_flags (status);
CREATE INDEX IF NOT EXISTS ix_ai_flags_student_id ON ai_flags (student_id);
CREATE INDEX IF NOT EXISTS ix_ai_flags_flag_type ON ai_flags (flag_type);
CREATE TABLE IF NOT EXISTS employer_profiles (
	user_id VARCHAR(36) NOT NULL, 
	company_name VARCHAR(200) NOT NULL, 
	logo_url VARCHAR(500), 
	website VARCHAR(255), 
	about TEXT, 
	industry VARCHAR(120), 
	location VARCHAR(160), 
	company_size VARCHAR(60), 
	is_featured BOOLEAN NOT NULL, 
	is_verified BOOLEAN NOT NULL, 
	id VARCHAR(36) NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE
);
CREATE UNIQUE INDEX IF NOT EXISTS ix_employer_profiles_user_id ON employer_profiles (user_id);
CREATE INDEX IF NOT EXISTS ix_employer_profiles_is_featured ON employer_profiles (is_featured);
CREATE TABLE IF NOT EXISTS opportunity_matches (
	student_id VARCHAR(36) NOT NULL, 
	opportunity_id VARCHAR(36) NOT NULL, 
	score FLOAT NOT NULL, 
	reasoning TEXT, 
	engine VARCHAR(60), 
	id VARCHAR(36) NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT uq_opportunity_match UNIQUE (student_id, opportunity_id), 
	FOREIGN KEY(student_id) REFERENCES students (id) ON DELETE CASCADE, 
	FOREIGN KEY(opportunity_id) REFERENCES opportunities (id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS ix_opportunity_matches_student_id ON opportunity_matches (student_id);
CREATE INDEX IF NOT EXISTS ix_opportunity_matches_opportunity_id ON opportunity_matches (opportunity_id);

