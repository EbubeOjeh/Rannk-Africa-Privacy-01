import { api } from './api';

/**
 * Public reporting / homepage feed API (no auth required).
 *  - `publicStats()` → headline platform counters for the stats band.
 *  - `homepage()`    → featured rankings, latest opportunities, employers.
 *
 * Both endpoints are read-only and intentionally tolerant: the landing page
 * falls back to its editable static content if either call fails or is empty.
 */
export const reportsService = {
  publicStats: () => api.get('/reports/public-stats').then((r) => r.data),
  homepage: () => api.get('/reports/homepage').then((r) => r.data),
};
