import { useState, useEffect } from 'react';
import { Outlet, Link, useLocation } from 'react-router-dom';
import { Bell, LogOut, Menu } from 'lucide-react';
import { Sidebar } from '@/components/Sidebar';
import { PendingBanner } from '@/components/PendingBanner';
import { useAuth } from '@/hooks/useAuth';
import { useLogout } from '@/hooks/useLogout';

export function AdminLayout() {
  const { user } = useAuth();
  const logout = useLogout();
  const [navOpen, setNavOpen] = useState(false);
  const location = useLocation();

  // Close the mobile drawer whenever the route changes.
  useEffect(() => setNavOpen(false), [location.pathname]);

  return (
    <div className="min-h-screen flex bg-ink-950">
      <Sidebar mobileOpen={navOpen} onClose={() => setNavOpen(false)} />
      <div className="flex-1 flex flex-col min-w-0">
        <header className="h-16 border-b border-cream/10 bg-ink-900/60 flex items-center justify-between gap-2 px-4 lg:px-8">
          <div className="flex items-center gap-3 min-w-0">
            <button
              className="btn-ghost h-9 w-9 p-0 lg:hidden shrink-0"
              onClick={() => setNavOpen(true)}
              aria-label="Open menu"
            >
              <Menu className="w-5 h-5" />
            </button>
            <div className="min-w-0">
              <p className="text-xs text-cream/50 uppercase tracking-wider truncate">
                {user?.role?.replace('_', ' ')}
                {user?.school_name ? ` · ${user.school_name}` : ''}
              </p>
              <h1 className="text-sm font-semibold text-white truncate">
                Welcome, {user?.name?.split(' ')[0] || 'Admin'}
              </h1>
            </div>
          </div>
          <div className="flex items-center gap-2 shrink-0">
            <button className="btn-ghost h-9 w-9 p-0">
              <Bell className="w-4 h-4" />
            </button>
            <Link to="/" className="btn-ghost text-xs hidden sm:inline-flex">View site</Link>
            <button onClick={logout} className="btn-ghost text-xs" aria-label="Sign out">
              <LogOut className="w-4 h-4" /> <span className="hidden sm:inline">Sign out</span>
            </button>
          </div>
        </header>
        <main className="flex-1 p-4 lg:p-8 overflow-y-auto">
          <PendingBanner />
          <Outlet />
        </main>
      </div>
    </div>
  );
}
