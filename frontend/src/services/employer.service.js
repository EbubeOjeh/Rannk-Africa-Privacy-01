import { api } from './api';

/**
 * Employer / recruiter surface. The backend mounts these under
 * `/api/v1/employers` (the shared `api` instance already carries that prefix).
 * Authorisation (approval gating, contact-unlock) is enforced server-side; the
 * frontend only mirrors it for presentation.
 */
export const employerService = {
  // Company profile. GET 404s when the employer hasn't created one yet — the
  // caller is expected to treat that as "no profile" rather than a hard error.
  getProfile: () => api.get('/employers/profile').then((r) => r.data),
  saveProfile: (payload) => api.put('/employers/profile', payload).then((r) => r.data),

  // Featured employers (used on the public-facing portal / homepage strips).
  featured: () => api.get('/employers/featured').then((r) => r.data),

  // Candidate search. `params` mirrors the documented query contract:
  // { q, university_id, field_id, min_score, max_score, graduation_year, skill, page, page_size }
  search: (params = {}) => api.get('/employers/search', { params }).then((r) => r.data),

  // Saved (shortlisted) candidates.
  saved: () => api.get('/employers/saved').then((r) => r.data),
  save: (studentId, notes) =>
    api.post(`/employers/saved/${studentId}`, { notes }).then((r) => r.data),
  unsave: (studentId) => api.delete(`/employers/saved/${studentId}`).then((r) => r.data),
};
