import { api } from './api';

// CEO/admin dummy test accounts (auto-deleted 20 days after creation).
export const testAccountsService = {
  list: () => api.get('/test-accounts').then((r) => r.data),
  create: (payload) => api.post('/test-accounts', payload).then((r) => r.data),
  block: (id) => api.post(`/test-accounts/${id}/block`).then((r) => r.data),
  unblock: (id) => api.post(`/test-accounts/${id}/unblock`).then((r) => r.data),
  remove: (id) => api.delete(`/test-accounts/${id}`).then((r) => r.data),
  purge: () => api.post('/test-accounts/purge').then((r) => r.data),
};
