/**
 * Deep-merge a saved CMS document over a page's code defaults.
 *
 * Arrays are replaced wholesale (an admin reordering or deleting cards must
 * win outright); objects merge key by key; anything else takes the override.
 *
 * This used to live in `landingDefaults.js` alongside the copy for the old
 * launching-soon landing page. That page was retired at launch, so only the
 * helper remains — keeping the file meant shipping stale "registrations open
 * August 3rd, 2026" copy in the production bundle.
 */
export function mergeContent(base, override) {
  if (override === undefined || override === null) return base;
  if (Array.isArray(base) || Array.isArray(override)) return override;
  if (
    typeof base === 'object' &&
    base !== null &&
    typeof override === 'object' &&
    override !== null
  ) {
    const out = { ...base };
    for (const key of Object.keys(override)) {
      out[key] = mergeContent(base[key], override[key]);
    }
    return out;
  }
  return override;
}
