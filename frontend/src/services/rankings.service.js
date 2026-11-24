import { api } from './api';

export const rankingsService = {
  students: (params = {}) =>
    api.get('/rankings/students', { params }).then((r) => r.data),
  universities: (params = {}) =>
    api.get('/rankings/universities', { params }).then((r) => r.data),
  // Per-field university ranking (PRS §8) — universities ranked by their
  // publicly-visible students' average score within the given field.
  universitiesByField: (fieldKey, limit = 50) =>
    api
      .get('/rankings/universities/by-field', { params: { field_key: fieldKey, limit } })
      .then((r) => r.data),
  platformStats: () => api.get('/analytics/platform').then((r) => r.data),
  adminDashboard: () => api.get('/analytics/dashboard').then((r) => r.data),
  recompute: () => api.post('/rankings/recompute').then((r) => r.data),
  // Historical archive (seasons)
  seasons: () => api.get('/rankings/seasons').then((r) => r.data),
  season: (label) => api.get('/rankings/season', { params: { label } }).then((r) => r.data),
  publishSeason: (label) => api.post('/rankings/seasons/publish', { label }).then((r) => r.data),
};
