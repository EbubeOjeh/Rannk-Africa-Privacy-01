-- ============================================================================
--  OPS · Temporarily make the rankings visible to logged-out visitors
--  Run in the Supabase SQL editor. Fully reversible — see PART C.
-- ============================================================================
--
--  WHY THIS FILE EXISTS
--  --------------------
--  Two INDEPENDENT conditions must both be true before an anonymous visitor
--  sees a single row on /rankings. Flipping only the first one leaves a page
--  that renders but is empty ("No students match your filters"), which reads
--  as broken rather than as locked:
--
--    1. site_content['rankings'].released = true
--       The admin release switch. Read by settings_service.get_rankings_release
--       and enforced server-side in api/v1/endpoints/rankings.py.
--       -> Normally toggled from /admin/settings ("Rankings release" card).
--          PART A below is the SQL equivalent, for when the UI is inconvenient.
--
--    2. students.is_publicly_visible = true, per student
--       Set in exactly two places in the app (approvals.py:66-73 and
--       cycle_service.transition), and BOTH require the student to belong to a
--       SubmissionCycle that is PUBLISHED or CLOSED. A self-registered student
--       whose submission_cycle_id is NULL can be APPROVED and still never
--       become visible — the admin UI has no path to fix that.
--       -> PART B handles it directly.
--
--  MEASURED PRODUCTION STATE (2026-08-04, via the public API):
--    /site/rankings        -> data {} (no row)  => released = false
--    /reports/public-stats -> registered_students = 0
--    /analytics/platform   -> total_students = 7, top_student_name = null
--  i.e. 7 student rows exist and NONE of them is publicly visible.
--
--  NOTE: staff accounts (SUPER_ADMIN / EMPLOYEE / EVALUATOR) can preview the
--  rankings even while released = false (rankings.py `_can_preview`). Always
--  verify in a LOGGED-OUT incognito window, or you will get a false positive.
-- ============================================================================


-- ─── PART 0 · AUDIT (read-only — run this first and read the output) ────────
SELECT count(*) FILTER (WHERE is_publicly_visible)                AS visible_now,
       count(*) FILTER (WHERE approval_status = 'APPROVED')       AS approved,
       count(*) FILTER (WHERE submission_cycle_id IS NULL)        AS no_cycle,
       count(*) FILTER (WHERE final_score IS NULL OR final_score = 0) AS unscored,
       count(*)                                                   AS total
  FROM students;

SELECT id, name, year, status FROM submission_cycles ORDER BY year DESC, name;

SELECT key FROM site_content WHERE key = 'rankings';   -- 0 rows = never set


-- ─── PART A · Release the rankings (same effect as the admin toggle) ────────
-- `data` is a JSON (not JSONB) column, and `key` carries a unique index, so an
-- upsert is safe whether or not the row already exists.
INSERT INTO site_content (id, key, data, created_at, updated_at)
VALUES (
  gen_random_uuid()::text,
  'rankings',
  '{"released": true, "message": "Rankings will be released in Q1 2027."}'::json,
  now(),
  now()
)
ON CONFLICT (key) DO UPDATE
  SET data = EXCLUDED.data,
      updated_at = now();


-- ─── PART B · Make the existing students publicly visible ───────────────────
--
-- PREFER THE ADMIN UI IF PART 0 SHOWS no_cycle = 0. The app has a supported
-- path that keeps the approval semantics intact:
--     a. /admin/approvals  → approve each student
--     b. /admin/cycles     → transition the cycle to PUBLISHED
--        (cycle_service.transition then flips is_publicly_visible for every
--         APPROVED student in that cycle, in bulk)
-- Legal transitions are DRAFT→OPEN→{REVIEW,PUBLISHED}→CLOSED, and note that
-- CLOSED also LOCKS the cycle and freezes scores — stop at PUBLISHED.
--
-- USE THE SQL BELOW WHEN PART 0 SHOWS no_cycle > 0. Students registered while
-- no cycle was OPEN have submission_cycle_id = NULL (auth_service.py:208), and
-- for them neither UI path can ever set the flag — approving such a student
-- actually forces is_publicly_visible back to false (approvals.py:73).
--
-- Reviewing "everything" means reviewing every registered student, so this
-- deliberately does NOT filter on approval_status. To show only students you
-- have actually approved, add:
--     AND approval_status = 'APPROVED'
UPDATE students
   SET is_publicly_visible = true
 WHERE is_publicly_visible = false;

-- University cards on /universities read denormalised aggregates that only the
-- ranking recompute refreshes. After running this, call (as super-admin):
--     POST /api/v1/rankings/recompute
-- so ranks, university averages and student_count are consistent. Without it
-- the student leaderboard populates but university rankings may still read 0.


-- ─── PART C · REVERT (run this when the review is finished) ─────────────────
-- Restores the launch state: rankings hidden, nobody publicly visible.
-- Safe to run as-is TODAY, because the audit above confirmed that zero students
-- were publicly visible before PART B — so "set them all back to false" is an
-- exact undo. If you run PART B again later, re-check PART 0 first.
--
-- UPDATE site_content
--    SET data = '{"released": false, "message": "Rankings will be released in Q1 2027."}'::json,
--        updated_at = now()
--  WHERE key = 'rankings';
--
-- UPDATE students SET is_publicly_visible = false;
--
-- (The release half can also simply be clicked off at /admin/settings →
--  "Hide rankings"; only the is_publicly_visible half needs this SQL.)
