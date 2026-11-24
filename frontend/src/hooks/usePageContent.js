import { useEffect, useState } from 'react';
import { siteService } from '@/services/site.service';
import { PAGE_DEFAULTS, STORAGE_KEYS, mergeContent } from '@/content/pageContent';
import { useEditContext } from '@/content/EditContext';
import { readSiteCache, writeSiteCache } from '@/lib/siteCache';

/**
 * Returns a page's content: the code defaults with any saved admin edits merged
 * on top. On the live site it fetches the saved document once; inside the editor
 * preview it uses the live (unsaved) draft, so edits show instantly.
 *
 * The defaults always render, so a missing document or a failed request still
 * shows the page — it never goes blank. The saved document is seeded
 * synchronously from the session cache so the page doesn't visibly re-render
 * from defaults to saved copy on every load (see lib/siteCache).
 */
export function usePageContent(pageKey) {
  const edit = useEditContext();
  const storageKey = STORAGE_KEYS[pageKey] || pageKey;
  const [remote, setRemote] = useState(() => readSiteCache(storageKey));

  useEffect(() => {
    if (edit) return; // preview mode — content comes from the editor draft
    let alive = true;
    siteService
      .get(storageKey)
      .then((res) => {
        if (res?.data && typeof res.data === 'object') {
          writeSiteCache(storageKey, res.data);
          if (alive) setRemote(res.data);
        }
      })
      .catch(() => {
        /* keep defaults — the page must always render */
      });
    return () => {
      alive = false;
    };
  }, [storageKey, edit]);

  const override = edit && edit.page === pageKey ? edit.draft : remote;
  return mergeContent(PAGE_DEFAULTS[pageKey] || {}, override || {});
}
