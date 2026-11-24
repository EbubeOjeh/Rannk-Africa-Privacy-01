-- RankAfrica — student unofficial-transcript upload + remove the Music discipline
-- ---------------------------------------------------------------------------
-- Run this WHOLE file ONCE in the Supabase SQL Editor on the PRODUCTION DB.
-- Idempotent & safe to re-run. (Follows migration_v3_scoring_applications.sql.)
-- ---------------------------------------------------------------------------

-- 1) Student-uploaded UNOFFICIAL transcript / semester results document URL.
ALTER TABLE students ADD COLUMN IF NOT EXISTS transcript_url VARCHAR(500);

-- 2) Remove the Music discipline for now (deferred to a future update). The MUSIC
--    slug + scoring code remain in the app (dormant) so it can be re-added later.
--    Reassign any Music students to Media & Communications (so they keep a valid
--    profile-model field rather than becoming field-less), clear it on any Music
--    opportunities, then drop the Music field row. No-op if Music is already gone.
UPDATE students
   SET field_id = (SELECT id FROM fields WHERE slug = 'media-communications')
 WHERE field_id = (SELECT id FROM fields WHERE slug = 'music');

UPDATE opportunities
   SET field_id = NULL
 WHERE field_id = (SELECT id FROM fields WHERE slug = 'music');

DELETE FROM fields WHERE slug = 'music';
