import { api } from './api';

/**
 * Student self-service API surface. The shared `api` instance already prefixes
 * `/api/v1`, so paths here are relative to that (e.g. `/me`, `/auth/...`).
 *
 * Every sub-entity (research, experience, competitions, leadership, projects,
 * achievements) exposes the same trio — `listX` / `addX` / `removeX` — so the
 * profile builder can treat them uniformly. Achievements `add` is multipart
 * (optional evidence file); the rest are plain JSON.
 */

// Shared multipart helper — mirrors the pattern in auth.service.uploadAvatar.
const upload = (url, file, field = 'file') => {
  const fd = new FormData();
  fd.append(field, file);
  return api
    .post(url, fd, { headers: { 'Content-Type': 'multipart/form-data' } })
    .then((r) => r.data);
};

export const studentService = {
  // ── Auth / onboarding ────────────────────────────────────────────────
  getTerms: () => api.get('/auth/terms').then((r) => r.data),
  register: (payload) => api.post('/auth/register-student', payload).then((r) => r.data),

  // ── Profile ──────────────────────────────────────────────────────────
  me: () => api.get('/me').then((r) => r.data),
  updateMe: (payload) => api.patch('/me', payload).then((r) => r.data),
  uploadAvatar: (file) => upload('/me/avatar', file),
  uploadResume: (file) => upload('/me/resume', file),
  uploadTranscript: (file) => upload('/me/transcript', file),
  dashboard: () => api.get('/me/dashboard').then((r) => r.data),

  // ── Research ─────────────────────────────────────────────────────────
  listResearch: () => api.get('/me/research').then((r) => r.data),
  addResearch: (payload) => api.post('/me/research', payload).then((r) => r.data),
  removeResearch: (id) => api.delete(`/me/research/${id}`).then((r) => r.data),

  // ── Experience ───────────────────────────────────────────────────────
  listExperience: () => api.get('/me/experience').then((r) => r.data),
  addExperience: (payload) => api.post('/me/experience', payload).then((r) => r.data),
  removeExperience: (id) => api.delete(`/me/experience/${id}`).then((r) => r.data),

  // ── Competitions ─────────────────────────────────────────────────────
  listCompetitions: () => api.get('/me/competitions').then((r) => r.data),
  addCompetition: (payload) => api.post('/me/competitions', payload).then((r) => r.data),
  removeCompetition: (id) => api.delete(`/me/competitions/${id}`).then((r) => r.data),

  // ── Leadership ───────────────────────────────────────────────────────
  listLeadership: () => api.get('/me/leadership').then((r) => r.data),
  addLeadership: (payload) => api.post('/me/leadership', payload).then((r) => r.data),
  removeLeadership: (id) => api.delete(`/me/leadership/${id}`).then((r) => r.data),

  // ── Projects ─────────────────────────────────────────────────────────
  listProjects: () => api.get('/me/projects').then((r) => r.data),
  addProject: (payload) => api.post('/me/projects', payload).then((r) => r.data),
  removeProject: (id) => api.delete(`/me/projects/${id}`).then((r) => r.data),
  evaluateProject: (id) => api.post(`/me/projects/${id}/evaluate`).then((r) => r.data),

  // ── Achievements (add = multipart, optional evidence file) ───────────
  listAchievements: () => api.get('/me/achievements').then((r) => r.data),
  addAchievement: ({ evidence, ...payload }) => {
    const fd = new FormData();
    Object.entries(payload).forEach(([k, v]) => {
      if (v !== undefined && v !== null && v !== '') fd.append(k, v);
    });
    if (evidence) fd.append('evidence', evidence);
    return api
      .post('/me/achievements', fd, { headers: { 'Content-Type': 'multipart/form-data' } })
      .then((r) => r.data);
  },
  removeAchievement: (id) => api.delete(`/me/achievements/${id}`).then((r) => r.data),
};
