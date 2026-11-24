import { api } from './api';

export const achievementsService = {
  catalog: () => api.get('/achievements/catalog').then((r) => r.data),
  forStudent: (studentId) =>
    api.get(`/achievements/by-student/${studentId}`).then((r) => r.data),
  submit: (studentId, { type, title, description, link, evidence }) => {
    const form = new FormData();
    form.append('type', type);
    form.append('title', title);
    if (description) form.append('description', description);
    if (link) form.append('link', link);
    if (evidence) form.append('evidence', evidence);
    return api
      .post(`/achievements/by-student/${studentId}`, form, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      .then((r) => r.data);
  },
  verify: (id, payload) =>
    api.post(`/achievements/${id}/verify`, payload).then((r) => r.data),
  remove: (id) => api.delete(`/achievements/${id}`).then((r) => r.data),
};
