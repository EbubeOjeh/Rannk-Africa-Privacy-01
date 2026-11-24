import { useState, useEffect } from 'react';
import { Outlet, NavLink, Navigate, useLocation } from 'react-router-dom';
import {
  LayoutDashboard,
  Search as SearchIcon,
  Bookmark,
  Briefcase,
  Building2,
  LogOut,
  Menu,
  X,
  Clock,
} from 'lucide-react';
import { Logo } from '@/components/Logo';
import { useAuth } from '@/hooks/useAuth';
import { useLogout } from '@/hooks/useLogout';

const NAV = [
  { to: '/employer', icon: LayoutDashboard, label: 'Dashboard', end: true },
  { to: '/employer/search', icon: SearchIcon, label: 'Search Students' },
  { to: '/employer/saved', icon: Bookmark, label: 'Saved' },
  { to: '/employer/opportunities', icon: Briefcase, label: 'Opportunities' },
  { to: '/employer/applications', icon: Briefcase, label: 'Applications' },
  { to: '/employer/profile', icon: Building2, label: 'Company' },
];

/**
 * Shell for the employer / recruiter portal. Top-nav (not the admin sidebar),
 * its own auth guard, and a pending notice while the account is unapproved —
 * contact unlock, candidate search and posting all open up after a RankAfrica
 * admin approves the employer.
 */
export default function EmployerLayout() {
  const { isAuthenticated, role, user } = useAuth();
  const logout = useLogout();
  const location = useLocation();
  const [open, setOpen] = useState(false);

  useEffect(() => setOpen(false), [location.pathname]);

  // Guard: only signed-in employers may enter.
  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }
  if (role !== 'employer') {
    return <Navigate to="/" replace />;
  }

  const approved = user?.approval_status === 'approved';

  const linkClass = ({ isActive }) =>
    `flex items-center gap-2 px-3 py-2 rounded-lg text-sm transition-colors ${
      isActive ? 'bg-gold-400/15 text-gold-300' : 'text-cream/70 hover:bg-cream/5 hover:text-white'
    }`;

  return (
    <div className="min-h-screen flex flex-col bg-ink-950">
      <header className="sticky top-0 z-40 h-16 border-b border-cream/10 bg-ink-900/70 backdrop-blur-md">
        <div className="container-page h-full flex items-center justify-between gap-3">
          <Logo to="/employer" />

          <nav className="hidden lg:flex items-center gap-1">
            {NAV.map((l) => (
              <NavLink key={l.to} to={l.to} end={l.end} className={linkClass}>
                <l.icon className="w-4 h-4" /> {l.label}
              </NavLink>
            ))}
          </nav>

          <div className="flex items-center gap-2 shrink-0">
            <span className="hidden sm:block text-xs text-cream/50 truncate max-w-[12rem]">
              {user?.company_name || user?.name || user?.email}
            </span>
            <button onClick={logout} className="btn-ghost text-xs" aria-label="Sign out">
              <LogOut className="w-4 h-4" /> <span className="hidden sm:inline">Sign out</span>
            </button>
            <button
              className="btn-ghost h-9 w-9 p-0 lg:hidden"
              onClick={() => setOpen((v) => !v)}
              aria-label="Toggle menu"
            >
              {open ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </button>
          </div>
        </div>

        {/* Mobile nav drawer */}
        {open && (
          <div className="lg:hidden border-t border-cream/10 bg-ink-900">
            <div className="container-page py-3 flex flex-col gap-1">
              {NAV.map((l) => (
                <NavLink key={l.to} to={l.to} end={l.end} className={linkClass}>
                  <l.icon className="w-4 h-4" /> {l.label}
                </NavLink>
              ))}
            </div>
          </div>
        )}
      </header>

      <main className="flex-1 container-page py-8">
        {!approved && (
          <div className="mb-6 rounded-xl border border-amber-400/30 bg-amber-500/10 px-4 py-3 flex items-start gap-3">
            <Clock className="w-5 h-5 text-amber-300 mt-0.5 shrink-0" />
            <div className="text-sm">
              <div className="font-semibold text-amber-200">
                Your recruiter account is awaiting RankAfrica approval.
              </div>
              <div className="text-amber-100/80 mt-0.5">
                You can set up your company profile now, but unlocking student contact details,
                full candidate search, and posting opportunities are enabled once a RankAfrica
                admin approves your account. Questions?{' '}
                <a href="mailto:info@rankafrica.org" className="underline">
                  info@rankafrica.org
                </a>
                .
              </div>
            </div>
          </div>
        )}
        <Outlet />
      </main>
    </div>
  );
}
