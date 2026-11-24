-- ============================================================================
-- RankAfrica — PRS v2.0 FIELDS reconciliation (run AFTER migration_prs_v2.sql).
-- Makes the `fields` table hold EXACTLY the 8 PRS disciplines (§4), remaps any
-- student/department on a legacy field to Technology, and removes the old
-- tech-only fields. Idempotent — safe to re-run.
-- Paste the WHOLE file into the Supabase SQL editor and Run.
-- ============================================================================

-- 1) Ensure the 8 canonical fields exist (no-op for any that already do).
INSERT INTO fields (id, name, slug, description, icon, color) VALUES
  (gen_random_uuid()::text, 'Law', 'law', 'Law, legal studies and jurisprudence.', 'scale', '#7c2d12'),
  (gen_random_uuid()::text, 'Technology', 'technology', 'Computing, software, data, AI and emerging technology.', 'cpu', '#1A3D2B'),
  (gen_random_uuid()::text, 'Medical Sciences', 'medical-sciences', 'Medicine, nursing, pharmacy and allied health sciences.', 'heart-pulse', '#b91c1c'),
  (gen_random_uuid()::text, 'Engineering', 'engineering', 'Civil, mechanical, electrical, chemical and other engineering.', 'wrench', '#3a6a4b'),
  (gen_random_uuid()::text, 'Architecture', 'architecture', 'Architecture, design and the built environment.', 'ruler', '#a05a1f'),
  (gen_random_uuid()::text, 'Music', 'music', 'Music, performance and the creative sound arts.', 'music', '#6d28d9'),
  (gen_random_uuid()::text, 'Business', 'business', 'Business, accounting, finance, economics and management.', 'briefcase', '#C47C2B'),
  (gen_random_uuid()::text, 'Media & Communications', 'media-communications', 'Journalism, mass communication, media and PR.', 'megaphone', '#0e7490')
ON CONFLICT DO NOTHING;

-- 2) Remap any student/department still pointing at a legacy field to Technology.
UPDATE students SET field_id = (SELECT id FROM fields WHERE slug = 'technology')
WHERE field_id IS NOT NULL
  AND field_id NOT IN (
    SELECT id FROM fields WHERE slug IN
      ('law','technology','medical-sciences','engineering','architecture','music','business','media-communications')
  );

UPDATE departments SET field_id = (SELECT id FROM fields WHERE slug = 'technology')
WHERE field_id IS NOT NULL
  AND field_id NOT IN (
    SELECT id FROM fields WHERE slug IN
      ('law','technology','medical-sciences','engineering','architecture','music','business','media-communications')
  );

-- 3) Remove the legacy fields (now unreferenced) so exactly 8 remain.
DELETE FROM fields WHERE slug NOT IN
  ('law','technology','medical-sciences','engineering','architecture','music','business','media-communications');
