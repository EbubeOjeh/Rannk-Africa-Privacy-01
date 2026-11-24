import { api } from './api';

export const recruitersService = {
  register: (payload) => api.post('/auth/register-recruiter', payload).then((r) => r.data),
  pending: () => api.get('/recruiters/pending').then((r) => r.data),
  list: (status) => api.get('/recruiters', { params: status ? { status } : {} }).then((r) => r.data),
  approve: (id) => api.post(`/recruiters/${id}/approve`).then((r) => r.data),
  reject: (id) => api.post(`/recruiters/${id}/reject`).then((r) => r.data),
};
