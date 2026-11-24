-- ============================================================================
-- RankAfrica — Supabase schema
-- Run this WHOLE file in the Supabase SQL Editor (Dashboard -> SQL -> New query).
-- It is safe to re-run: enum types are guarded, and tables/indexes use
-- IF NOT EXISTS. It creates every table the backend expects, plus one
-- super-admin login so you can sign in immediately.
--
-- Default super-admin (CHANGE THE PASSWORD after first login):
--   email:    admin@rankafrica.org
--   password: ChangeMe123!
-- ============================================================================

DO $$ BEGIN
  CREATE TYPE achievement_type AS ENUM ('INTERNSHIP', 'HACKATHON_PARTICIPATION', 'HACKATHON_WIN', 'LEADERSHIP_ROLE', 'PUBLICATION', 'STARTUP_BUILT', 'AWARD', 'CERTIFICATION', 'SCHOLARSHIP', 'GRANT', 'FELLOWSHIP', 'NATIONAL_RECOGNITION');
EXCEPTION WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
  CREATE TYPE verification_status AS ENUM ('UNVERIFIED', 'VERIFIED', 'REJECTED');
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

DO $$ BEGIN
  CREATE TYPE competition_type AS ENUM ('HACKATHON', 'MOOT_COURT', 'BUSINESS_COMPETITION', 'DEBATE', 'MUSIC_AWARD', 'INNOVATION_CHALLENGE');
EXCEPTION WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
  CREATE TYPE competition_result AS ENUM ('WINNER', 'RUNNER_UP', 'FINALIST', 'PARTICIPANT');
EXCEPTION WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
  CREATE TYPE contact_message_status AS ENUM ('PENDING', 'SENT', 'FAILED', 'BLOCKED');
EXCEPTION WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
  CREATE TYPE experience_type AS ENUM ('INTERNSHIP', 'VOLUNTEER', 'STARTUP', 'BUSINESS', 'EMPLOYMENT');
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
  CREATE TYPE application_status AS ENUM ('RECEIVED', 'REVIEWED', 'SHORTLISTED', 'REJECTED', 'SELECTED');
EXCEPTION WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
  CREATE TYPE project_status AS ENUM ('PENDING', 'EVALUATED', 'MODERATED', 'FAILED');
EXCEPTION WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
  CREATE TYPE research_type AS ENUM ('JOURNAL_PUBLICATION', 'CONFERENCE_PAPER', 'UNDERGRADUATE_RESEARCH', 'RESEARCH_ASSISTANTSHIP', 'BOOK_CHAPTER');
EXCEPTION WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
  CREATE TYPE approval_status AS ENUM ('PENDING', 'APPROVED', 'REJECTED');
EXCEPTION WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
  CREATE TYPE cycle_status AS ENUM ('DRAFT', 'OPEN', 'REVIEW', 'PUBLISHED', 'CLOSED');
EXCEPTION WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
  CREATE TYPE school_approval_status AS ENUM ('PENDING', 'APPROVED', 'REJECTED');
EXCEPTION WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
  CREATE TYPE user_role AS ENUM ('SUPER_ADMIN', 'SCHOOL_ADMIN', 'UNIVERSITY_ADMIN', 'STUDENT', 'EMPLOYER', 'EVALUATOR', 'EMPLOYEE');
EXCEPTION WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
  CREATE TYPE user_approval_status AS ENUM ('PENDING', 'APPROVED', 'REJECTED');
EXCEPTION WHEN duplicate_object THEN null;
END $$;

CREATE TABLE IF NOT EXISTS fields (
	name VARCHAR(80) NOT NULL, 
	slug VARCHAR(80) NOT NULL, 
	description TEXT, 
	icon VARCHAR(50), 
	color VARCHAR(20), 
	id VARCHAR(36) NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE UNIQUE INDEX IF NOT EXISTS ix_fields_name ON fields (name);

CREATE UNIQUE INDEX IF NOT EXISTS ix_fields_slug ON fields (slug);

CREATE TABLE IF NOT EXISTS ranking_snapshots (
	scope VARCHAR(40) NOT NULL, 
	scope_key VARCHAR(120), 
	total_entities INTEGER NOT NULL, 
	payload JSON, 
	id VARCHAR(36) NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE INDEX IF NOT EXISTS ix_ranking_snapshots_scope ON ranking_snapshots (scope);

CREATE INDEX IF NOT EXISTS ix_ranking_snapshots_scope_key ON ranking_snapshots (scope_key);

CREATE TABLE IF NOT EXISTS roles (
	name VARCHAR(80) NOT NULL, 
	description VARCHAR(300), 
	permissions JSON NOT NULL, 
	is_system BOOLEAN NOT NULL, 
	id VARCHAR(36) NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE UNIQUE INDEX IF NOT EXISTS ix_roles_name ON roles (name);

CREATE TABLE IF NOT EXISTS site_content (
	key VARCHAR(80) NOT NULL, 
	data JSON NOT NULL, 
	id VARCHAR(36) NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE UNIQUE INDEX IF NOT EXISTS ix_site_content_key ON site_content (key);

CREATE TABLE IF NOT EXISTS submission_cycles (
	name VARCHAR(120) NOT NULL, 
	year INTEGER NOT NULL, 
	submission_opens_at TIMESTAMP WITH TIME ZONE, 
	submission_closes_at TIMESTAMP WITH TIME ZONE, 
	review_ends_at TIMESTAMP WITH TIME ZONE, 
	published_at TIMESTAMP WITH TIME ZONE, 
	closed_at TIMESTAMP WITH TIME ZONE, 
	status cycle_status NOT NULL, 
	is_locked BOOLEAN NOT NULL, 
	max_students_per_school INTEGER NOT NULL, 
	description TEXT, 
	id VARCHAR(36) NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	UNIQUE (name)
);

CREATE INDEX IF NOT EXISTS ix_submission_cycles_status ON submission_cycles (status);

CREATE INDEX IF NOT EXISTS ix_submission_cycles_year ON submission_cycles (year);

CREATE TABLE IF NOT EXISTS universities (
	name VARCHAR(200) NOT NULL, 
	slug VARCHAR(220) NOT NULL, 
	short_name VARCHAR(50), 
	country VARCHAR(80) NOT NULL, 
	state VARCHAR(80), 
	city VARCHAR(120), 
	website VARCHAR(255), 
	logo_url VARCHAR(500), 
	description TEXT, 
	domain VARCHAR(120), 
	grading_system VARCHAR(50) NOT NULL, 
	accreditation_type VARCHAR(80), 
	institution_type VARCHAR(20) NOT NULL, 
	tier INTEGER NOT NULL, 
	approval_status school_approval_status NOT NULL, 
	approval_notes VARCHAR(500), 
	approved_at TIMESTAMP WITH TIME ZONE, 
	approved_by_id VARCHAR(36), 
	avg_score FLOAT NOT NULL, 
	top_score FLOAT NOT NULL, 
	elite_student_count INTEGER NOT NULL, 
	student_count INTEGER NOT NULL, 
	overall_rank INTEGER, 
	id VARCHAR(36) NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE INDEX IF NOT EXISTS ix_universities_country ON universities (country);

CREATE UNIQUE INDEX IF NOT EXISTS ix_universities_domain ON universities (domain);

CREATE UNIQUE INDEX IF NOT EXISTS ix_universities_name ON universities (name);

CREATE INDEX IF NOT EXISTS ix_universities_state ON universities (state);

CREATE INDEX IF NOT EXISTS ix_universities_approval_status ON universities (approval_status);

CREATE INDEX IF NOT EXISTS ix_universities_overall_rank ON universities (overall_rank);

CREATE UNIQUE INDEX IF NOT EXISTS ix_universities_slug ON universities (slug);

CREATE INDEX IF NOT EXISTS ix_universities_institution_type ON universities (institution_type);

CREATE TABLE IF NOT EXISTS faculties (
	name VARCHAR(160) NOT NULL, 
	university_id VARCHAR(36) NOT NULL, 
	id VARCHAR(36) NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT uq_faculty_uni_name UNIQUE (university_id, name), 
	FOREIGN KEY(university_id) REFERENCES universities (id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS ix_faculties_university_id ON faculties (university_id);

CREATE TABLE IF NOT EXISTS users (
	name VARCHAR(160) NOT NULL, 
	email VARCHAR(255) NOT NULL, 
	password_hash VARCHAR(255) NOT NULL, 
	role user_role NOT NULL, 
	is_active BOOLEAN NOT NULL, 
	is_email_verified BOOLEAN NOT NULL, 
	approval_status user_approval_status DEFAULT 'APPROVED' NOT NULL, 
	must_change_password BOOLEAN NOT NULL, 
	is_test_account BOOLEAN DEFAULT false NOT NULL, 
	avatar_url VARCHAR(500), 
	title VARCHAR(120), 
	university_id VARCHAR(36), 
	company_role_id VARCHAR(36), 
	organization VARCHAR(200), 
	suspension_reason VARCHAR(500), 
	suspended_at TIMESTAMP WITH TIME ZONE, 
	id VARCHAR(36) NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(university_id) REFERENCES universities (id) ON DELETE SET NULL, 
	FOREIGN KEY(company_role_id) REFERENCES roles (id) ON DELETE SET NULL
);

CREATE UNIQUE INDEX IF NOT EXISTS ix_users_email ON users (email);

CREATE TABLE IF NOT EXISTS audit_logs (
	actor_id VARCHAR(36), 
	actor_email VARCHAR(255), 
	action VARCHAR(80) NOT NULL, 
	entity_type VARCHAR(60), 
	entity_id VARCHAR(60), 
	ip_address VARCHAR(64), 
	metadata JSON, 
	id VARCHAR(36) NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(actor_id) REFERENCES users (id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS ix_audit_logs_entity_type ON audit_logs (entity_type);

CREATE INDEX IF NOT EXISTS ix_audit_logs_action ON audit_logs (action);

CREATE INDEX IF NOT EXISTS ix_audit_logs_entity_id ON audit_logs (entity_id);

CREATE INDEX IF NOT EXISTS ix_audit_logs_actor_id ON audit_logs (actor_id);

CREATE TABLE IF NOT EXISTS departments (
	name VARCHAR(160) NOT NULL, 
	university_id VARCHAR(36) NOT NULL, 
	faculty_id VARCHAR(36), 
	field_id VARCHAR(36), 
	avg_score FLOAT NOT NULL, 
	id VARCHAR(36) NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT uq_dept_uni_name UNIQUE (university_id, name), 
	FOREIGN KEY(university_id) REFERENCES universities (id) ON DELETE CASCADE, 
	FOREIGN KEY(faculty_id) REFERENCES faculties (id) ON DELETE SET NULL, 
	FOREIGN KEY(field_id) REFERENCES fields (id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS ix_departments_field_id ON departments (field_id);

CREATE INDEX IF NOT EXISTS ix_departments_faculty_id ON departments (faculty_id);

CREATE INDEX IF NOT EXISTS ix_departments_university_id ON departments (university_id);

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

CREATE TABLE IF NOT EXISTS notifications (
	user_id VARCHAR(36) NOT NULL, 
	title VARCHAR(200) NOT NULL, 
	body TEXT, 
	link VARCHAR(500), 
	is_read BOOLEAN NOT NULL, 
	category VARCHAR(40) NOT NULL, 
	id VARCHAR(36) NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS ix_notifications_user_id ON notifications (user_id);

CREATE INDEX IF NOT EXISTS ix_notifications_is_read ON notifications (is_read);

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

CREATE INDEX IF NOT EXISTS ix_opportunities_type ON opportunities (type);

CREATE INDEX IF NOT EXISTS ix_opportunities_field_id ON opportunities (field_id);

CREATE INDEX IF NOT EXISTS ix_opportunities_posted_by_id ON opportunities (posted_by_id);

CREATE INDEX IF NOT EXISTS ix_opportunities_is_active ON opportunities (is_active);

CREATE TABLE IF NOT EXISTS students (
	full_name VARCHAR(180) NOT NULL, 
	email VARCHAR(255), 
	phone_number VARCHAR(40), 
	linkedin_url VARCHAR(500), 
	matric_number VARCHAR(80), 
	gender VARCHAR(20), 
	avatar_url VARCHAR(500), 
	academic_level INTEGER, 
	year_of_study INTEGER, 
	bio VARCHAR(1600), 
	profile_statement TEXT, 
	course VARCHAR(200), 
	faculty VARCHAR(200), 
	skills JSON, 
	languages JSON, 
	resume_url VARCHAR(500), 
	transcript_url VARCHAR(500), 
	portfolio_url VARCHAR(500), 
	github_url VARCHAR(500), 
	behance_url VARCHAR(500), 
	google_scholar_url VARCHAR(500), 
	music_url VARCHAR(500), 
	whatsapp_number VARCHAR(40), 
	user_id VARCHAR(36), 
	is_self_registered BOOLEAN NOT NULL, 
	terms_accepted_at TIMESTAMP WITH TIME ZONE, 
	raw_gpa FLOAT, 
	raw_cgpa FLOAT, 
	gpa_scale FLOAT NOT NULL, 
	normalized_cgpa FLOAT, 
	standardized_gpa_4 FLOAT, 
	class_of_degree VARCHAR(40), 
	credits_earned INTEGER NOT NULL, 
	academic_score FLOAT NOT NULL, 
	project_score FLOAT NOT NULL, 
	achievement_score FLOAT NOT NULL, 
	profile_score FLOAT NOT NULL, 
	research_score FLOAT NOT NULL, 
	leadership_score FLOAT NOT NULL, 
	experience_score FLOAT NOT NULL, 
	competition_score FLOAT NOT NULL, 
	final_score FLOAT NOT NULL, 
	standardized_score FLOAT NOT NULL, 
	consistency_score FLOAT NOT NULL, 
	overall_rank INTEGER, 
	field_rank INTEGER, 
	university_rank INTEGER, 
	department_rank INTEGER, 
	submission_cycle_id VARCHAR(36), 
	approval_status approval_status NOT NULL, 
	is_publicly_visible BOOLEAN NOT NULL, 
	approval_notes VARCHAR(500), 
	approved_at TIMESTAMP WITH TIME ZONE, 
	approved_by_id VARCHAR(36), 
	university_id VARCHAR(36) NOT NULL, 
	department_id VARCHAR(36), 
	field_id VARCHAR(36), 
	id VARCHAR(36) NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE SET NULL, 
	FOREIGN KEY(submission_cycle_id) REFERENCES submission_cycles (id) ON DELETE SET NULL, 
	FOREIGN KEY(approved_by_id) REFERENCES users (id) ON DELETE SET NULL, 
	FOREIGN KEY(university_id) REFERENCES universities (id) ON DELETE CASCADE, 
	FOREIGN KEY(department_id) REFERENCES departments (id) ON DELETE SET NULL, 
	FOREIGN KEY(field_id) REFERENCES fields (id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS ix_students_matric_number ON students (matric_number);

CREATE INDEX IF NOT EXISTS ix_students_is_publicly_visible ON students (is_publicly_visible);

CREATE INDEX IF NOT EXISTS ix_students_final_score ON students (final_score);

CREATE INDEX IF NOT EXISTS ix_students_university_id ON students (university_id);

CREATE INDEX IF NOT EXISTS ix_students_email ON students (email);

CREATE INDEX IF NOT EXISTS ix_students_field_id ON students (field_id);

CREATE INDEX IF NOT EXISTS ix_students_standardized_score ON students (standardized_score);

CREATE INDEX IF NOT EXISTS ix_students_submission_cycle_id ON students (submission_cycle_id);

CREATE INDEX IF NOT EXISTS ix_students_full_name ON students (full_name);

CREATE INDEX IF NOT EXISTS ix_students_department_id ON students (department_id);

CREATE INDEX IF NOT EXISTS ix_students_user_id ON students (user_id);

CREATE INDEX IF NOT EXISTS ix_students_overall_rank ON students (overall_rank);

CREATE INDEX IF NOT EXISTS ix_students_approval_status ON students (approval_status);

CREATE TABLE IF NOT EXISTS achievements (
	student_id VARCHAR(36) NOT NULL, 
	type achievement_type NOT NULL, 
	points INTEGER NOT NULL, 
	title VARCHAR(240) NOT NULL, 
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

CREATE INDEX IF NOT EXISTS ix_achievements_type ON achievements (type);

CREATE INDEX IF NOT EXISTS ix_achievements_student_id ON achievements (student_id);

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

CREATE INDEX IF NOT EXISTS ix_ai_flags_student_id ON ai_flags (student_id);

CREATE INDEX IF NOT EXISTS ix_ai_flags_status ON ai_flags (status);

CREATE INDEX IF NOT EXISTS ix_ai_flags_flag_type ON ai_flags (flag_type);

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

CREATE INDEX IF NOT EXISTS ix_competitions_type ON competitions (type);

CREATE INDEX IF NOT EXISTS ix_competitions_student_id ON competitions (student_id);

CREATE TABLE IF NOT EXISTS contact_messages (
	student_id VARCHAR(36) NOT NULL, 
	sender_name VARCHAR(160) NOT NULL, 
	sender_email VARCHAR(255) NOT NULL, 
	sender_organization VARCHAR(200), 
	sender_role VARCHAR(120), 
	subject VARCHAR(200) NOT NULL, 
	message TEXT NOT NULL, 
	status contact_message_status NOT NULL, 
	sent_at TIMESTAMP WITH TIME ZONE, 
	failure_reason TEXT, 
	id VARCHAR(36) NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(student_id) REFERENCES students (id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS ix_contact_messages_student_id ON contact_messages (student_id);

CREATE INDEX IF NOT EXISTS ix_contact_messages_sender_email ON contact_messages (sender_email);

CREATE TABLE IF NOT EXISTS evaluation_results (
	student_id VARCHAR(36) NOT NULL, 
	engine_version VARCHAR(20) NOT NULL, 
	academic_score FLOAT NOT NULL, 
	project_score FLOAT NOT NULL, 
	achievement_score FLOAT NOT NULL, 
	final_score FLOAT NOT NULL, 
	normalized_gpa FLOAT NOT NULL, 
	consistency_score FLOAT NOT NULL, 
	weighted_score FLOAT NOT NULL, 
	inflation_penalty FLOAT NOT NULL, 
	standardized_score FLOAT NOT NULL, 
	breakdown JSON, 
	id VARCHAR(36) NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(student_id) REFERENCES students (id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS ix_evaluation_results_final_score ON evaluation_results (final_score);

CREATE INDEX IF NOT EXISTS ix_evaluation_results_student_id ON evaluation_results (student_id);

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

CREATE INDEX IF NOT EXISTS ix_leadership_activities_student_id ON leadership_activities (student_id);

CREATE INDEX IF NOT EXISTS ix_leadership_activities_type ON leadership_activities (type);

CREATE TABLE IF NOT EXISTS opportunity_applications (
	opportunity_id VARCHAR(36) NOT NULL, 
	student_id VARCHAR(36) NOT NULL, 
	status application_status NOT NULL, 
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

CREATE TABLE IF NOT EXISTS project_submissions (
	student_id VARCHAR(36) NOT NULL, 
	title VARCHAR(240) NOT NULL, 
	description TEXT NOT NULL, 
	problem_statement TEXT, 
	report_url VARCHAR(500), 
	source_code_url VARCHAR(500), 
	demo_video_url VARCHAR(500), 
	originality FLOAT NOT NULL, 
	technical_depth FLOAT NOT NULL, 
	problem_solving FLOAT NOT NULL, 
	innovation FLOAT NOT NULL, 
	total_score FLOAT NOT NULL, 
	status project_status NOT NULL, 
	ai_engine VARCHAR(40), 
	ai_reasoning JSON, 
	moderator_notes TEXT, 
	evaluated_at TIMESTAMP WITH TIME ZONE, 
	moderated_at TIMESTAMP WITH TIME ZONE, 
	id VARCHAR(36) NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(student_id) REFERENCES students (id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS ix_project_submissions_student_id ON project_submissions (student_id);

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

CREATE INDEX IF NOT EXISTS ix_terms_acceptances_student_id ON terms_acceptances (student_id);

CREATE INDEX IF NOT EXISTS ix_terms_acceptances_user_id ON terms_acceptances (user_id);

-- ---------------------------------------------------------------------------
-- SEED: super-admin login (no demo data). Password is bcrypt-hashed.
-- Re-running does nothing if the email already exists.
-- ---------------------------------------------------------------------------
INSERT INTO users (id, name, email, password_hash, role, is_active, is_email_verified, must_change_password)
VALUES (
  '00000000-0000-0000-0000-000000000001',
  'Super Admin',
  'admin@rankafrica.org',
  '$2b$12$DzYaMj828Y5.bnP7FXD3OOKT95p.7SxP/nekvPypPtEIZ20yQjqoe',
  'SUPER_ADMIN',
  true,
  true,
  false
)
ON CONFLICT (email) DO NOTHING;

-- ---------------------------------------------------------------------------
-- SEED: company roles + staff accounts (password 'rankpass', must change on
-- first login). Re-running is a no-op (ON CONFLICT).
-- ---------------------------------------------------------------------------
INSERT INTO roles (id, name, description, permissions, is_system) VALUES
  (gen_random_uuid()::text, 'Chief Executive Officer', 'Overall leadership, vision, partnerships and major decisions.', '["full_access"]'::json, true),
  (gen_random_uuid()::text, 'Chief Technology Officer', 'Technology, engineering and platform direction.', '["full_access"]'::json, true),
  (gen_random_uuid()::text, 'Chief Operating Officer', 'Operations, project management, team coordination and execution.', '["view_analytics", "manage_cycles", "approve_students"]'::json, true),
  (gen_random_uuid()::text, 'Chief Marketing Officer', 'Marketing, branding, social media, PR and growth.', '["manage_site", "view_analytics"]'::json, true),
  (gen_random_uuid()::text, 'Chief Partnerships Officer', 'University, corporate, government and NGO partnerships.', '["approve_recruiters", "view_analytics"]'::json, true),
  (gen_random_uuid()::text, 'Chief Programs Officer', 'Internship programs, student engagement and impact measurement.', '["approve_students", "view_analytics"]'::json, true)
ON CONFLICT (name) DO NOTHING;

INSERT INTO users (id, name, email, password_hash, role, is_active, is_email_verified, must_change_password, title, company_role_id) VALUES
  (gen_random_uuid()::text, 'Kennedy', 'kennedy@rankafrica.org', '$2b$12$16KUXCprgut9jt6rFZ9AWec.G7YnxIutqNorms5UC8Tc4P2DUCG8m', 'SUPER_ADMIN', true, true, true, 'Chief Executive Officer', (SELECT id FROM roles WHERE name = 'Chief Executive Officer')),
  (gen_random_uuid()::text, 'Austin', 'austin@rankafrica.org', '$2b$12$16KUXCprgut9jt6rFZ9AWec.G7YnxIutqNorms5UC8Tc4P2DUCG8m', 'EMPLOYEE', true, true, true, 'Chief Operating Officer', (SELECT id FROM roles WHERE name = 'Chief Operating Officer')),
  (gen_random_uuid()::text, 'Ike', 'ike@rankafrica.org', '$2b$12$16KUXCprgut9jt6rFZ9AWec.G7YnxIutqNorms5UC8Tc4P2DUCG8m', 'EMPLOYEE', true, true, true, 'Chief Marketing Officer', (SELECT id FROM roles WHERE name = 'Chief Marketing Officer')),
  (gen_random_uuid()::text, 'Josh', 'josh@rankafrica.org', '$2b$12$16KUXCprgut9jt6rFZ9AWec.G7YnxIutqNorms5UC8Tc4P2DUCG8m', 'EMPLOYEE', true, true, true, 'Chief Partnerships Officer', (SELECT id FROM roles WHERE name = 'Chief Partnerships Officer')),
  (gen_random_uuid()::text, 'Benjamin', 'benjamin@rankafrica.org', '$2b$12$16KUXCprgut9jt6rFZ9AWec.G7YnxIutqNorms5UC8Tc4P2DUCG8m', 'EMPLOYEE', true, true, true, 'Chief Programs Officer', (SELECT id FROM roles WHERE name = 'Chief Programs Officer'))
ON CONFLICT (email) DO NOTHING;

-- The technical admin also represents the CTO on the public team page.
UPDATE users SET name = 'Offia Victory', title = 'Chief Technology Officer', company_role_id = (SELECT id FROM roles WHERE name = 'Chief Technology Officer') WHERE email = 'admin@rankafrica.org' AND company_role_id IS NULL;
