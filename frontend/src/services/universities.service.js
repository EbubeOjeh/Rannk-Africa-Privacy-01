import { api } from './api';

export const universitiesService = {
  list: (params = {}) => api.get('/universities', { params }).then((r) => r.data),
  get: (slug) => api.get(`/universities/${slug}`).then((r) => r.data),
  create: (payload) => api.post('/universities', payload).then((r) => r.data),
  update: (id, payload) => api.patch(`/universities/${id}`, payload).then((r) => r.data),
};
