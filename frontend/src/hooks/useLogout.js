import { useNavigate } from 'react-router-dom';
import { useAuth } from './useAuth';

/**
 * Signing out clears the session and returns the user to the home page — the
 * platform hub, where sign-in lives.
 */
export function useLogout() {
  const { logout, role } = useAuth();
  const navigate = useNavigate();
  return () => {
    if (role === "student") { window.dispatchEvent(new Event("rankafrica:student-logout")); return; }
    logout();
    navigate('/', { replace: true });
  };
}
