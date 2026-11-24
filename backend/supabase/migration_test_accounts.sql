-- RankAfrica — dummy test accounts (CEO/admin-created, auto-deleted after 20 days)
--
-- Prod DB is hand-applied. Run this ONCE in the Supabase SQL editor. Idempotent.
--
-- It (1) adds the users.is_test_account flag and (2) schedules a daily pg_cron
-- job that permanently deletes any test account older than 20 days (its linked
-- student + all that student's data cascade away via ON DELETE CASCADE).
--
-- The app also purges expired test accounts opportunistically (whenever the
-- admin opens the Test Accounts page, and on any login attempt), so the pg_cron
-- job is a belt-and-braces guarantee that they leave the database on schedule
-- even if no admin visits.

-- 1) Flag column ------------------------------------------------------------
ALTER TABLE users
  ADD COLUMN IF NOT EXISTS is_test_account BOOLEAN NOT NULL DEFAULT false;

-- 2) Daily auto-delete via pg_cron -----------------------------------------
-- pg_cron ships with Supabase; enable it once (Dashboard → Database →
-- Extensions → search "pg_cron" → enable), or the CREATE EXTENSION below.
CREATE EXTENSION IF NOT EXISTS pg_cron;

-- Re-running is safe: unschedule the old job first if it exists.
DO $$
BEGIN
  PERFORM cron.unschedule('purge-expired-test-accounts');
EXCEPTION WHEN OTHERS THEN
  -- job didn't exist yet — ignore.
  NULL;
END $$;

-- Run every day at 03:00 UTC. Deletes the linked students first (children
-- cascade), then the users. 20 days == the test-account TTL.
SELECT cron.schedule(
  'purge-expired-test-accounts',
  '0 3 * * *',
  $$
    DELETE FROM students
     WHERE user_id IN (
       SELECT id FROM users
        WHERE is_test_account = true
          AND created_at < now() - interval '20 days'
     );
    DELETE FROM users
     WHERE is_test_account = true
       AND created_at < now() - interval '20 days';
  $$
);

-- To confirm it's scheduled:  SELECT * FROM cron.job;
