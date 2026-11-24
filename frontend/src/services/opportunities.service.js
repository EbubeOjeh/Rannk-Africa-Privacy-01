import { api } from './api';

/**
 * Opportunities (internships, graduate jobs, scholarships, research,
 * competitions, leadership programs). Public reads + employer-authored writes,
 * plus a student-only AI recommendation feed. Mounted under `/api/v1/opportunities`.
 */
export const opportunitiesService = {
  // Public browse. `params`: { type?, field_id?, q?, active_only? }
  list: (params = {}) => api.get('/opportunities', { params }).then((r) => r.data),
  get: (id) => api.get(`/opportunities/${id}`).then((r) => r.data),

  // Employer-authored mutations.
  create: (payload) => api.post('/opportunities', payload).then((r) => r.data),
  update: (id, payload) => api.patch(`/opportunities/${id}`, payload).then((r) => r.data),
  close: (id) => api.post(`/opportunities/${id}/close`).then((r) => r.data),
  remove: (id) => api.delete(`/opportunities/${id}`).then((r) => r.data),

  // Student-only: AI-matched opportunities → [{ opportunity, score, reasoning }]
  recommended: () => api.get('/opportunities/me/recommended').then((r) => r.data),

  // Applications.
  apply: (id, confirmation) => api.post(`/opportunities/${id}/apply`, confirmation).then((r) => r.data),
  myApplications: () => api.get('/opportunities/me/applications').then((r) => r.data),
  applicants: (id) => api.get(`/opportunities/${id}/applicants`).then((r) => r.data),
};
