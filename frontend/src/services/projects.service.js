import { api } from './api';

export const projectsService = {
  forStudent: (studentId) =>
    api.get(`/projects/by-student/${studentId}`).then((r) => r.data),
  upsert: (studentId, payload) =>
    api.post(`/projects/by-student/${studentId}`, payload).then((r) => r.data),
  uploadFiles: (studentId, { report, demo, sourceCodeUrl }, onProgress) => {
    const form = new FormData();
    if (report) form.append('report', report);
    if (demo) form.append('demo_video', demo);
    if (sourceCodeUrl) form.append('source_code_url', sourceCodeUrl);
    return api
      .post(`/projects/by-student/${studentId}/files`, form, {
        headers: { 'Content-Type': 'multipart/form-data' },
        onUploadProgress: (e) => onProgress?.(Math.round((e.loaded / (e.total || 1)) * 100)),
      })
      .then((r) => r.data);
  },
  evaluate: (studentId) =>
    api.post(`/projects/by-student/${studentId}/evaluate`).then((r) => r.data),
  moderate: (studentId, payload) =>
    api.post(`/projects/by-student/${studentId}/moderate`, payload).then((r) => r.data),
  remove: (studentId) =>
    api.delete(`/projects/by-student/${studentId}`).then((r) => r.data),
};
