import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '@/hooks/useAuth';

const CHANGE_PW_PATH = '/admin/change-password';

export function ProtectedRoute({ children, roles }) {
  const { isAuthenticated, role, mustChangePassword } = useAuth();
  const location = useLocation();

  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }
  // Recruiters/employers and students have their own dashboards — the admin
  // app isn't for them.
  if (role === 'employer') {
    return <Navigate to="/employer" replace />;
  }
  if (role === 'student') {
    return <Navigate to="/student" replace />;
  }
  // First login: everyone must set a new password before using the app.
  if (mustChangePassword && location.pathname !== CHANGE_PW_PATH) {
    return <Navigate to={CHANGE_PW_PATH} replace />;
  }
  if (roles && !roles.includes(role)) {
    return <Navigate to="/" replace />;
  }
  return children;
}

/** Gate a single admin route on a fine-grained permission. */
export function RequirePermission({ permission, children }) {
  const { can } = useAuth();
  if (!can(permission)) {
    return <Navigate to="/admin" replace />;
  }
  return children;
}
