import { api } from './api';

export const studentsService = {
  list: (params = {}) => api.get('/students', { params }).then((r) => r.data),
  get: (id) => api.get(`/students/${id}`).then((r) => r.data),
  // Full public v2 profile (PRS §9): scores, ranks, badges, projects, etc.
  full: (id) => api.get(`/students/${id}/full`).then((r) => r.data),
  create: (payload) => api.post('/students', payload).then((r) => r.data),
  update: (id, payload) => api.patch(`/students/${id}`, payload).then((r) => r.data),
  remove: (id) => api.delete(`/students/${id}`).then((r) => r.data),
  uploadAvatar: (id, file) => {
    const form = new FormData();
    form.append('file', file);
    return api
      .post(`/students/${id}/avatar`, form, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      .then((r) => r.data);
  },
};
