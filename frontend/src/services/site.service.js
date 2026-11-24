import { api } from './api';

/**
 * Site content (CMS) API.
 *  - `get(key)` is public — used by the landing page.
 *  - `update(key, data)` is gated server-side on the `manage_site` permission
 *    (CEO + technical admin).
 */
export const siteService = {
  get: (key) => api.get(`/site/${key}`).then((r) => r.data),
  update: (key, data) => api.put(`/site/${key}`, { data }).then((r) => r.data),

  // Convenience wrappers for the landing document.
  getLanding: () => api.get('/site/landing').then((r) => r.data),
  updateLanding: (data) => api.put('/site/landing', { data }).then((r) => r.data),
};
