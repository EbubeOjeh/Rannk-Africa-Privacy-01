-- ============================================================================
--  OPS · Pre-launch account reset  ·  ⚠ DESTRUCTIVE AND IRREVERSIBLE ⚠
-- ============================================================================
--
--  Deletes every student and recruiter/employer account and all of their data,
--  so the platform launches with a clean database. KEEPS the admin/team logins
--  and all reference + CMS data, so nobody is locked out and the public site
--  still renders.
--
--  DO NOT RUN THIS UNTIL THE RANKINGS REVIEW IS FINISHED —
--  it empties the leaderboard that ops_rankings_public_preview.sql exposes.
--
--  TAKE A BACKUP FIRST. Supabase Dashboard → Database → Backups. Note the PITR
--  timestamp. There is no application-level undo: password hashes go with the
--  rows, so every deleted student and recruiter must re-register from scratch.
--
--  ── Why the order below is not negotiable ─────────────────────────────────
--  `students.user_id` is ON DELETE **SET NULL**, not CASCADE (schema.sql:452).
--  Deleting from `users` therefore does NOT remove student profiles — it just
--  orphans them. Students must be deleted FIRST, independently.
--
--  ⚠ NEVER add `universities` to this script. `students.university_id` is
--  ON DELETE CASCADE (schema.sql:455), so deleting a university silently
--  destroys its students. Universities are reference data — they stay.
--
--  ⚠ Do NOT use TRUNCATE (it ignores the ordering that makes this safe) and do
--  NOT run `python -m app.db.seed`, which drops every table and reseeds ~200
--  FAKE students — that produces a demo database, not a clean one.
-- ============================================================================


-- ─── STEP 0 · AUDIT (read-only). Run alone. Eyeball before going further. ───
-- The survivors are decided purely by role. If a teammate holds EVALUATOR, or
-- an admin was created under a personal address, they WILL be deleted unless
-- you adjust the role list in step 1c.
SELECT role, count(*) FROM users GROUP BY role ORDER BY 2 DESC;

SELECT id, name, email, role
  FROM users
 WHERE role IN ('SUPER_ADMIN', 'EMPLOYEE')      -- <<< THESE SURVIVE. Confirm.
 ORDER BY created_at;

SELECT (SELECT count(*) FROM students)     AS students,
       (SELECT count(*) FROM universities) AS universities,
       (SELECT count(*) FROM fields)       AS fields,
       (SELECT count(*) FROM opportunities) AS opportunities,
       (SELECT count(*) FROM site_content) AS cms_docs;

-- Legacy/optional tables: NULL means the migration never reached prod, which is
-- fine — the guarded block in step 1a handles either case.
SELECT to_regclass('public.opportunity_applications') AS opp_applications,
       to_regclass('public.transcripts')              AS transcripts,
       to_regclass('public.transcript_courses')       AS transcript_courses;


-- ─── STEP 1 · THE WIPE (one transaction) ───────────────────────────────────
BEGIN;

-- 1a. Legacy tables dropped from the app but possibly still present in prod.
--     Guarded so a missing table cannot abort the transaction.
DO $$
BEGIN
  IF to_regclass('public.transcript_courses') IS NOT NULL THEN
    EXECUTE 'DELETE FROM transcript_courses';
  END IF;
  IF to_regclass('public.transcripts') IS NOT NULL THEN
    EXECUTE 'DELETE FROM transcripts';
  END IF;
END $$;

-- 1b. Every student profile.
--     ON DELETE CASCADE clears all 13 child tables in one statement:
--       achievements, ai_flags, student_badges, competitions, contact_messages,
--       evaluation_results, experiences, leadership_activities,
--       opportunity_applications, opportunity_matches, project_submissions,
--       research_publications, saved_candidates.
DELETE FROM students;

-- 1c. Every non-staff account.
--     CASCADE clears employer_profiles and notifications.
--     Keeps SUPER_ADMIN + EMPLOYEE — the admin/team logins.
DELETE FROM users
 WHERE role IN ('STUDENT', 'EMPLOYER', 'EVALUATOR', 'SCHOOL_ADMIN', 'UNIVERSITY_ADMIN');

-- 1d. SET NULL orphans and derived data that CASCADE cannot reach.
DELETE FROM terms_acceptances;  -- consent records; both FKs are SET NULL
DELETE FROM notifications;      -- incl. admin alerts about deleted recruiters
DELETE FROM ranking_snapshots;  -- archived leaderboards naming deleted students
-- DELETE FROM audit_logs;      -- OPTIONAL: uncomment for a fully clean slate.
                                -- Keeping it preserves the pre-launch action
                                -- history (actor_id becomes NULL, actor_email
                                -- is retained on the row).

-- 1e. Reset denormalised aggregates that DELETE does not touch.
UPDATE universities
   SET student_count = 0, avg_score = 0, top_score = 0,
       elite_student_count = 0, overall_rank = NULL;
UPDATE departments SET avg_score = 0;

-- 1f. Re-home opportunities whose poster was a deleted recruiter
--     (opportunities.posted_by_id is SET NULL, so the listing survives).
UPDATE opportunities
   SET posted_by_id = (SELECT id FROM users WHERE role = 'SUPER_ADMIN'
                        ORDER BY created_at LIMIT 1)
 WHERE posted_by_id IS NULL;


-- ─── STEP 2 · VERIFY BEFORE YOU COMMIT ─────────────────────────────────────
SELECT (SELECT count(*) FROM students)      AS students_left,       -- expect 0
       (SELECT count(*) FROM users)         AS users_left,          -- expect the staff count from STEP 0
       (SELECT count(*) FROM universities)  AS universities_kept,   -- expect ~61, NOT 0
       (SELECT count(*) FROM fields)        AS fields_kept,         -- expect 7
       (SELECT count(*) FROM roles)         AS roles_kept,
       (SELECT count(*) FROM site_content)  AS cms_docs_kept,       -- unchanged
       (SELECT count(*) FROM opportunities) AS opportunities_kept;  -- unchanged

COMMIT;
-- ...or ROLLBACK; if any number above surprises you.


-- ─── STEP 3 · AFTER COMMIT ─────────────────────────────────────────────────
--  1. Sign in as the super-admin and confirm it works BEFORE closing your
--     session. This is the lockout check.
--  2. Supabase → Storage → the uploads bucket: the deleted rows were the only
--     pointers to those files, so delete resumes/, transcripts/, projects/ and
--     achievements/ wholesale, and everything under avatars/ except the
--     surviving staff ids. Otherwise ex-users' CVs stay world-readable.
--  3. Confirm a SubmissionCycle exists and is OPEN — students are stamped with
--     the active cycle at registration (auth_service.py:208) and get NULL if
--     there isn't one, which later blocks them from ever becoming publicly
--     visible.
--  4. Rotate the seeded staff passwords before launch.
--
--  ── WHAT IS IRREVERSIBLY LOST ─────────────────────────────────────────────
--  All student accounts + profiles (CGPA, scores, ranks, profile_statement,
--  skills, links, contact details); all projects with their AI rubric scores
--  and reasoning; research, experience, competitions, leadership, achievements,
--  badges, AI integrity flags and the full evaluation history; all employer
--  accounts, company profiles and saved shortlists; the recruiter→student
--  contact_messages archive; all terms_acceptances (the legal record of T&C
--  consent, with IP and user-agent); notifications; ranking_snapshots; every
--  password hash; and every uploaded avatar, CV, transcript and evidence file.
--
--  ── WHAT IS PRESERVED ─────────────────────────────────────────────────────
--  Admin/team logins (SUPER_ADMIN + EMPLOYEE), roles, universities, fields,
--  faculties, departments, ALL site_content (every page's CMS copy, the scoring
--  weights and the rankings-release switch), submission_cycles, opportunities.
