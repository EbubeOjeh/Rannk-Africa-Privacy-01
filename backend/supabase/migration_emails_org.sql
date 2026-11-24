-- ============================================================================
-- RankAfrica — Move all team/admin emails from @rankafrica.com to @rankafrica.org
-- Run this WHOLE file in the Supabase SQL Editor. Safe to re-run.
-- Updates the admin and all seeded staff accounts (kennedy@, austin@, ike@,
-- josh@, benjamin@) so they log in with their @rankafrica.org address.
-- ============================================================================

UPDATE users
SET email = replace(email, '@rankafrica.com', '@rankafrica.org')
WHERE email LIKE '%@rankafrica.com';
