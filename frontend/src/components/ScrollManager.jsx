import { useEffect, useLayoutEffect } from 'react';
import { useLocation, useNavigationType } from 'react-router-dom';

/**
 * Scroll behaviour for client-side navigation.
 *
 * `<BrowserRouter>` does nothing about scroll on its own (react-router's
 * `<ScrollRestoration>` only works with a data router), so the app kept the
 * previous page's scroll offset when you followed a link: clicking "See the
 * full student rankings" from halfway down the home page dropped you into the
 * middle of the leaderboard, and going back landed you somewhere unrelated.
 *
 *  - Following a link (PUSH/REPLACE) starts the new page at the top.
 *  - Back/forward (POP) restores where you actually were on that entry.
 *
 * Positions are keyed by `location.key`, which react-router assigns per history
 * entry — so the same path visited twice restores independently.
 */
const positions = new Map();

export function ScrollManager() {
  const location = useLocation();
  const navigationType = useNavigationType();

  // Take manual control; otherwise the browser also tries to restore scroll on
  // popstate and fights the effect below.
  useEffect(() => {
    const previous = window.history.scrollRestoration;
    if (previous) window.history.scrollRestoration = 'manual';
    return () => {
      if (previous) window.history.scrollRestoration = previous;
    };
  }, []);

  // Track the scroll offset for the current history entry as the user moves.
  useEffect(() => {
    const key = location.key;
    const onScroll = () => positions.set(key, window.scrollY);
    window.addEventListener('scroll', onScroll, { passive: true });
    return () => {
      // Record the final position for this entry before leaving it.
      positions.set(key, window.scrollY);
      window.removeEventListener('scroll', onScroll);
    };
  }, [location.key]);

  useLayoutEffect(() => {
    if (navigationType === 'POP') {
      window.scrollTo(0, positions.get(location.key) ?? 0);
    } else {
      window.scrollTo(0, 0);
    }
  }, [location.key, navigationType]);

  return null;
}
