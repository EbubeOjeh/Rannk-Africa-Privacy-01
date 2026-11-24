-- ============================================================================
-- RankAfrica — Team seed (STEP 2 of 2)
-- Run this AFTER migration_team.sql has finished (it needs the new 'EMPLOYEE'
-- role value to be committed first — that's why this is a separate step).
--
-- Seeds the 5 staff accounts. Every account's password is 'rankpass' and they
-- must change it on first login. Emails self-correct once each person fills in
-- their full name. Safe to re-run (ON CONFLICT does nothing).
-- ============================================================================

INSERT INTO users (id, name, email, password_hash, role, is_active, is_email_verified, must_change_password, title, company_role_id) VALUES
  (gen_random_uuid()::text, 'Kennedy',  'kennedy@rankafrica.org',  '$2b$12$6ozhek8JNL2Ol1MuE2oCJeX7Aj4weK3Ooin0U18Le61Qx1j7.nTGa', 'SUPER_ADMIN', true, true, true, 'CEO',                          (SELECT id FROM roles WHERE name = 'CEO')),
  (gen_random_uuid()::text, 'Austin',   'austin@rankafrica.org',   '$2b$12$6ozhek8JNL2Ol1MuE2oCJeX7Aj4weK3Ooin0U18Le61Qx1j7.nTGa', 'EMPLOYEE',    true, true, true, 'COO',                          (SELECT id FROM roles WHERE name = 'COO')),
  (gen_random_uuid()::text, 'Ike',      'ike@rankafrica.org',      '$2b$12$6ozhek8JNL2Ol1MuE2oCJeX7Aj4weK3Ooin0U18Le61Qx1j7.nTGa', 'EMPLOYEE',    true, true, true, 'CMO',                          (SELECT id FROM roles WHERE name = 'CMO')),
  (gen_random_uuid()::text, 'Josh',     'josh@rankafrica.org',     '$2b$12$6ozhek8JNL2Ol1MuE2oCJeX7Aj4weK3Ooin0U18Le61Qx1j7.nTGa', 'EMPLOYEE',    true, true, true, 'Chief Partnerships Officer',   (SELECT id FROM roles WHERE name = 'Chief Partnerships Officer')),
  (gen_random_uuid()::text, 'Benjamin', 'benjamin@rankafrica.org', '$2b$12$6ozhek8JNL2Ol1MuE2oCJeX7Aj4weK3Ooin0U18Le61Qx1j7.nTGa', 'EMPLOYEE',    true, true, true, 'Chief Programs Officer',       (SELECT id FROM roles WHERE name = 'Chief Programs Officer'))
ON CONFLICT (email) DO NOTHING;
