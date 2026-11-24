import { useEffect, useState } from 'react';
import { siteService } from '@/services/site.service';
import { readSiteCache, writeSiteCache } from '@/lib/siteCache';

export const DEFAULT_RELEASE_MESSAGE =
  'Rankings will be released after the registration period closes. Follow our social media channels to be notified as soon as they are published.';

const CACHE_KEY = 'rankings';

/**
 * Reads the admin-controlled "rankings release" switch (site_content 'rankings').
 *
 *  - The last known value is seeded synchronously from the session cache, so a
 *    reload paints the correct state on the first frame instead of showing the
 *    locked state and then swapping to the released one.
 *  - With no cached value we assume LOCKED, so real rankings never flash before
 *    the gate resolves. `loading` stays true until the fetch settles, letting
 *    callers render a neutral placeholder rather than committing to "hidden".
 *  - On a fetch error we fail OPEN (let the backend — the authoritative gate —
 *    decide) rather than wrongly hiding rankings that have been released.
 */
export function useRankingsRelease() {
  const [state, setState] = useState(() => {
    const cached = readSiteCache(CACHE_KEY);
    return {
      // Nothing is known yet on a cold load, so callers can hold off on
      // rendering either branch; a warm cache is treated as settled.
      loading: !cached,
      released: !!cached?.released,
      message: cached?.message || DEFAULT_RELEASE_MESSAGE,
    };
  });

  useEffect(() => {
    let alive = true;
    siteService
      .get(CACHE_KEY)
      .then((res) => {
        const data = res?.data || {};
        writeSiteCache(CACHE_KEY, data);
        if (!alive) return;
        setState({
          loading: false,
          released: !!data.released,
          message: data.message || DEFAULT_RELEASE_MESSAGE,
        });
      })
      .catch(
        () =>
          alive &&
          setState({ loading: false, released: true, message: DEFAULT_RELEASE_MESSAGE })
      );
    return () => {
      alive = false;
    };
  }, []);

  return state;
}
