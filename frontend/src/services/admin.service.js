import { api } from './api';

// Admin v2.0 surfaces — integrity flags, profile-item verification, scoring
// weights, platform reports, user moderation and opportunity management.
// All endpoints sit under the shared `/api/v1` prefix on `api`.
export const adminService = {
  // FLAGS — AI integrity review queue (PRS §7, §13)
  flags: (params = {}) => api.get('/flags', { params }).then((r) => r.data),
  flagStats: () => api.get('/flags/stats').then((r) => r.data),
  scanStudent: (id) => api.post(`/flags/scan/${id}`).then((r) => r.data),
  resolveFlag: (id, payload) =>
    api.post(`/flags/${id}/resolve`, payload).then((r) => r.data),

  // VERIFICATION — pending profile-item verification (PRS §13)
  pendingVerifications: () =>
    api.get('/verification/pending').then((r) => r.data),
  verifyItem: (kind, id, payload) =>
    api.post(`/verification/${kind}/${id}`, payload).then((r) => r.data),

  // SCORING — adjustable category weights driving the /100 score (PRS §6, §13)
  getWeights: () => api.get('/scoring/weights').then((r) => r.data),
  saveWeights: (payload) =>
    api.put('/scoring/weights', payload).then((r) => r.data),

  // REPORTS — platform-wide report (PRS §13)
  platformReport: () => api.get('/reports/platform').then((r) => r.data),

  // MODERATION — suspend / unsuspend platform users (PRS §13)
  suspendedUsers: () => api.get('/admin-users/suspended').then((r) => r.data),
  suspendUser: (id, reason) =>
    api
      .post(`/admin-users/${id}/suspend`, { reason: reason || null })
      .then((r) => r.data),
  unsuspendUser: (id) =>
    api.post(`/admin-users/${id}/unsuspend`).then((r) => r.data),

  // OPPORTUNITIES — manage all opportunities (active + inactive)
  adminOpportunities: () =>
    api
      .get('/opportunities', { params: { active_only: false } })
      .then((r) => r.data),
  closeOpportunity: (id) =>
    api.post(`/opportunities/${id}/close`).then((r) => r.data),
  deleteOpportunity: (id) =>
    api.delete(`/opportunities/${id}`).then((r) => r.data),
  createOpportunity: (payload) =>
    api.post('/opportunities', payload).then((r) => r.data),
  opportunityApplicants: (id) =>
    api.get(`/opportunities/${id}/applicants`).then((r) => r.data),
};
