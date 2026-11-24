import { api } from './api';

export const cyclesService = {
  list: () => api.get('/cycles').then((r) => r.data),
  active: () => api.get('/cycles/active').then((r) => r.data),
  published: () => api.get('/cycles/published').then((r) => r.data),
  get: (id) => api.get(`/cycles/${id}`).then((r) => r.data),
  create: (payload) => api.post('/cycles', payload).then((r) => r.data),
  update: (id, payload) => api.patch(`/cycles/${id}`, payload).then((r) => r.data),
  setStatus: (id, status) =>
    api.post(`/cycles/${id}/status`, { status }).then((r) => r.data),
  remove: (id) => api.delete(`/cycles/${id}`).then((r) => r.data),
};
