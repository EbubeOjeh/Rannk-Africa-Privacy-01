import axios from 'axios';
import { useAuthStore } from '@/store/auth.store';

const baseURL =
  import.meta.env.VITE_API_BASE_URL || `${window.location.origin}/api/v1`;

export const api = axios.create({
  baseURL,
  timeout: 20000,
});

api.interceptors.request.use((config) => {
  const token = useAuthStore.getState().tokens?.access_token;
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

let refreshInFlight = null;

api.interceptors.response.use(
  (r) => r,
  async (error) => {
    const original = error.config;
    const isRefreshCall = original?.url?.includes('/auth/refresh');
    if (
      error?.response?.status === 401 &&
      !original?._retry &&
      !isRefreshCall &&
      useAuthStore.getState().tokens?.refresh_token
    ) {
      original._retry = true;
      try {
        if (!refreshInFlight) {
          refreshInFlight = api
            .post('/auth/refresh', {
              refresh_token: useAuthStore.getState().tokens.refresh_token,
            })
            .then((res) => res.data)
            .finally(() => {
              refreshInFlight = null;
            });
        }
        const tokens = await refreshInFlight;
        useAuthStore.getState().setTokens(tokens);
        original.headers.Authorization = `Bearer ${tokens.access_token}`;
        return api(original);
      } catch (e) {
        useAuthStore.getState().logout();
        return Promise.reject(e);
      }
    }
    return Promise.reject(error);
  }
);
