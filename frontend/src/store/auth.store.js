import { create } from 'zustand';
// Remove credentials left by earlier builds. Refresh deliberately requires login.
try { localStorage.removeItem('rankafrica-auth'); } catch { /* storage disabled */ }
export const useAuthStore = create((set) => ({
  user: null, tokens: null,
  setSession: ({ user, tokens }) => set({ user, tokens }),
  setTokens: (tokens) => set({ tokens }),
  setUser: (user) => set({ user }),
  logout: () => set({ user: null, tokens: null }),
}));
