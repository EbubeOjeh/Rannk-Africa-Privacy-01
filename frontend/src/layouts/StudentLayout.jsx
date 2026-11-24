import { useState } from 'react';
import { NavLink, Navigate, Outlet, useNavigate } from 'react-router-dom';
import { LayoutDashboard, User, Briefcase, LogOut, Menu, X } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { Logo } from '@/components/Logo';
import { useAuth } from '@/hooks/useAuth';
import { useLogout } from '@/hooks/useLogout';

const LINKS = [
  { to: '/student', label: 'Dashboard', icon: LayoutDashboard, end: true },
  { to: '/student/profile', label: 'My Profile', icon: User },
  { to: '/student/study', label: 'Study tasks', icon: User },
  { to: '/student/questionnaire', label: 'Questionnaire', icon: Briefcase },
  { to: '/student/privacy', label: 'Privacy', icon: User },
  { to: '/student/applications', label: 'Applications', icon: Briefcase },
  { to: '/opportunities', label: 'Opportunities', icon: Briefcase },
];

/**
 * Top-nav shell for the student self-service area. Guards on auth + the
 * `student` role; anyone else is bounced to the sign-in page.
 */
export default function StudentLayout() {
  const { isAuthenticated, role, user, logout } = useAuth();
  const signOut = useLogout();
  const [open, setOpen] = useState(false);

  if (!isAuthenticated || role !== 'student') {
    return <Navigate to="/login" replace />;
  }


  const linkClass = ({ isActive }) =>
    `flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
      isActive
        ? 'bg-gold-400/15 text-gold-300'
        : 'text-white/75 hover:text-white hover:bg-white/5'
    }`;

  return (
    <div className="min-h-screen flex flex-col bg-ink-950">
      <header className="sticky top-0 z-40 bg-ink-950/85 backdrop-blur-md border-b border-white/5">
        <div className="container-page flex items-center justify-between h-16 gap-4">
          <Logo to="/student" />

          <nav className="hidden md:flex items-center gap-1">
            {LINKS.map((l) => (
              <NavLink key={l.to} to={l.to} end={l.end} className={linkClass}>
                <l.icon className="w-4 h-4" />
                {l.label}
              </NavLink>
            ))}
          </nav>

          <div className="hidden md:flex items-center gap-3">
            <span className="text-xs text-cream/60 max-w-[10rem] truncate">
              {user?.name || user?.full_name || 'Student'}
            </span>
            <button onClick={signOut} className="btn-ghost text-xs" title="Sign out">
              <LogOut className="w-4 h-4" /> Sign out
            </button>
          </div>

          <button
            className="md:hidden btn-ghost h-9 w-9 p-0"
            onClick={() => setOpen((v) => !v)}
            aria-label="Toggle menu"
          >
            {open ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </button>
        </div>

        <AnimatePresence>
          {open && (
            <motion.div
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: 'auto', opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              className="md:hidden overflow-hidden border-t border-white/5"
            >
              <div className="container-page py-3 flex flex-col gap-1">
                {LINKS.map((l) => (
                  <NavLink
                    key={l.to}
                    to={l.to}
                    end={l.end}
                    className={linkClass}
                    onClick={() => setOpen(false)}
                  >
                    <l.icon className="w-4 h-4" />
                    {l.label}
                  </NavLink>
                ))}
                <button
                  onClick={signOut}
                  className="flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium text-white/75 hover:text-white hover:bg-white/5"
                >
                  <LogOut className="w-4 h-4" /> Sign out
                </button>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </header>

      <main className="flex-1">
        <div className="container-page py-8">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
