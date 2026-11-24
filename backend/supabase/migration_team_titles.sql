-- ============================================================================
-- RankAfrica — Full role titles + CTO on the team page
-- Run this WHOLE file in the Supabase SQL Editor. Safe to re-run.
-- 1) Renames abbreviated roles to their full titles.
-- 2) Updates staff job titles to match.
-- 3) Adds a "Chief Technology Officer" role and tags the admin account as the
--    CTO so it shows on the public Team page (no separate login needed).
-- ============================================================================

-- 1. Roles -> full names (no-op if already renamed).
UPDATE roles SET name = 'Chief Executive Officer' WHERE name = 'CEO';
UPDATE roles SET name = 'Chief Operating Officer'  WHERE name = 'COO';
UPDATE roles SET name = 'Chief Marketing Officer'  WHERE name = 'CMO';

-- 2. Staff titles -> full names.
UPDATE users SET title = 'Chief Executive Officer'  WHERE email = 'kennedy@rankafrica.org';
UPDATE users SET title = 'Chief Operating Officer'   WHERE email = 'austin@rankafrica.org';
UPDATE users SET title = 'Chief Marketing Officer'   WHERE email = 'ike@rankafrica.org';
UPDATE users SET title = 'Chief Partnerships Officer' WHERE email = 'josh@rankafrica.org';
UPDATE users SET title = 'Chief Programs Officer'    WHERE email = 'benjamin@rankafrica.org';

-- 3. CTO role + tag the admin account as the CTO.
INSERT INTO roles (id, name, description, permissions, is_system) VALUES
  (gen_random_uuid()::text, 'Chief Technology Officer', 'Technology, engineering and platform direction.', '["full_access"]'::json, true)
ON CONFLICT (name) DO NOTHING;

UPDATE users
SET name = 'Offia Victory',
    title = 'Chief Technology Officer',
    company_role_id = (SELECT id FROM roles WHERE name = 'Chief Technology Officer')
WHERE email = 'admin@rankafrica.org';
