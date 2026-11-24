import { api } from './api';

export const contactService = {
  send: (studentId, payload) =>
    api.post(`/contact/students/${studentId}`, payload).then((r) => r.data),
  inbox: (studentId) =>
    api.get(`/contact/students/${studentId}`).then((r) => r.data),
};
