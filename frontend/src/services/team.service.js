import { api } from './api';

export const teamService = {
  // Members
  list: () => api.get('/team').then((r) => r.data),
  create: (payload) => api.post('/team', payload).then((r) => r.data),
  update: (id, payload) => api.patch(`/team/${id}`, payload).then((r) => r.data),
  remove: (id) => api.delete(`/team/${id}`).then((r) => r.data),

  // Roles
  listRoles: () => api.get('/team/roles').then((r) => r.data),
  createRole: (payload) => api.post('/team/roles', payload).then((r) => r.data),
  updateRole: (id, payload) => api.patch(`/team/roles/${id}`, payload).then((r) => r.data),
  removeRole: (id) => api.delete(`/team/roles/${id}`).then((r) => r.data),

  // Catalog + public roster
  permissions: () => api.get('/team/permissions').then((r) => r.data),
  publicTeam: () => api.get('/team/public').then((r) => r.data),
};
