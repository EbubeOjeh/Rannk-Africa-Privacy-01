import { useAuthStore } from '@/store/auth.store';

export function useAuth() {
  const { user, tokens, setSession, setUser, logout } = useAuthStore();
  const permissions = user?.permissions || [];
  const can = (perm) => permissions.includes('full_access') || permissions.includes(perm);
  return {
    user,
    tokens,
    isAuthenticated: Boolean(user && tokens?.access_token),
    role: user?.role,
    permissions,
    can,
    mustChangePassword: Boolean(user?.must_change_password),
    setSession,
    setUser,
    logout,
  };
}
