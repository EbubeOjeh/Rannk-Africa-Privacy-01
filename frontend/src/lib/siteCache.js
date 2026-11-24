/**
 * A tiny session-scoped cache for `site_content` documents.
 *
 * Both `usePageContent` and `useRankingsRelease` fetch a document on mount and
 * render a placeholder until it lands. That made every page load visibly render
 * twice — the homepage showed the code-default hero and a "Coming soon" state,
 * then swapped to the saved copy and the real rankings a moment later, which
 * reads as two different pages flashing past.
 *
 * Seeding the hooks synchronously from this cache means the second and every
 * later load in a session paints the final content on the first frame. The
 * network request still runs and refreshes the cache, so edits made in the
 * admin site editor still show up — just without the flash.
 *
 * sessionStorage (not localStorage) is deliberate: the cache dies with the tab,
 * so a returning visitor never sees genuinely stale content.
 */
const PREFIX = 'ra:site:';

export function readSiteCache(key) {
  try {
    const raw = sessionStorage.getItem(PREFIX + key);
    if (!raw) return null;
    const parsed = JSON.parse(raw);
    return parsed && typeof parsed === 'object' ? parsed : null;
  } catch {
    // Private mode, quota, or corrupt JSON — the cache is an optimisation only.
    return null;
  }
}

export function writeSiteCache(key, data) {
  try {
    if (data && typeof data === 'object') {
      sessionStorage.setItem(PREFIX + key, JSON.stringify(data));
    }
  } catch {
    /* ignore */
  }
}
