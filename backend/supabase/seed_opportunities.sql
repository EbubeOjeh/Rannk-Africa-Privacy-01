-- RankAfrica — add the JEF Consulting-sponsored Toastmasters opportunity to production.
--
-- Prod data is hand-applied (there is no migration runner for the Supabase DB).
-- Run this ONCE in the Supabase SQL editor. It is idempotent — the NOT EXISTS
-- guard means re-running it will not create duplicates.
--
-- Any future opportunity is better added from the admin dashboard
-- (/admin/opportunities → "Post opportunity"); this file exists only to seed the
-- specific opportunity requested before the admin UI is used in production.

INSERT INTO opportunities (
  id, posted_by_id, organization, type, title, description,
  location, requirements, is_active, is_featured, created_at, updated_at
)
SELECT
  gen_random_uuid()::text,
  (SELECT id FROM users WHERE role = 'SUPER_ADMIN' ORDER BY created_at LIMIT 1),
  'JEF Consulting',
  'LEADERSHIP_PROGRAM',
  'Toastmasters 1-Year Subscription',
  'A fully sponsored one-year Toastmasters membership, paid for by JEF Consulting, '
    || 'to help you build world-class public speaking and leadership skills.',
  'Abuja',
  'Open to students based in Abuja.',
  true,
  true,
  now(),
  now()
WHERE NOT EXISTS (
  SELECT 1 FROM opportunities WHERE title = 'Toastmasters 1-Year Subscription'
);
