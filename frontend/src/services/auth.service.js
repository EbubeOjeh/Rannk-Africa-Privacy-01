import { api } from './api';

export const authService = {
  login: (email, password) => api.post('/auth/login', { email, password }).then((r) => r.data),
  signup: (payload) => api.post('/auth/signup', payload).then((r) => r.data),
  me: () => api.get('/auth/me').then((r) => r.data),

  changePassword: (current_password, new_password) =>
    api.post('/auth/change-password', { current_password, new_password }).then((r) => r.data),

  updateProfile: (payload) => api.patch('/users/me', payload).then((r) => r.data),

  uploadAvatar: (file) => {
    const fd = new FormData();
    fd.append('file', file);
    return api
      .post('/users/me/avatar', fd, { headers: { 'Content-Type': 'multipart/form-data' } })
      .then((r) => r.data);
  },
};
