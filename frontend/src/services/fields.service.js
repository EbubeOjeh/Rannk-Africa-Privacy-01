import { api } from './api';

export const fieldsService = {
  list: () => api.get('/fields').then((r) => r.data),
  get: (slug) => api.get(`/fields/${slug}`).then((r) => r.data),
};
