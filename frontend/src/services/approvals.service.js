import { api } from './api';

export const approvalsService = {
  pending: (params = {}) =>
    api.get('/approvals/pending', { params }).then((r) => r.data),
  set: (studentId, { status, notes }) =>
    api
      .post(`/approvals/${studentId}`, {
        approval_status: status,
        approval_notes: notes || null,
      })
      .then((r) => r.data),
};
