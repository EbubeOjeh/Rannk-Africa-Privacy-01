import { NavLink } from 'react-router-dom';
import { AnimatePresence, motion } from 'framer-motion';
import {
  LayoutDashboard,
  Upload,
  Users,
  BarChart3,
  History,
  Building2,
  Settings as SettingsIcon,
  Trophy,
  Calendar,
  ClipboardCheck,
  UserPlus,
  ShieldCheck,
  Briefcase,
  UserCog,
  UserCircle,
  FlaskConical,
  LayoutTemplate,
  Flag,
  BadgeCheck,
  SlidersHorizontal,
  FileBarChart,
  ShieldBan,
  Megaphone,
  Lock,
  X,
} from 'lucide-react';
import { Logo } from './Logo';
import { useAuth } from '@/hooks/useAuth';
import { SCHOOL_ADMIN_ROLES } from '@/utils/constants';

// Each link is shown when it has no `perm` (always) or the user `can(perm)`.
// `write` links are locked for a school admin whose school isn't approved yet.
const LINKS = [
  { to: '/admin', icon: LayoutDashboard, label: 'Overview', end: true },
  { to: '/admin/recruiters', icon: Briefcase, label: 'Recruiters', perm: 'approve_recruiters' },
  { to: '/admin/scores', icon: Trophy, label: 'Evaluated Scores', perm: 'view_analytics' },
  { to: '/admin/departments', icon: Building2, label: 'Field Rankings', perm: 'view_analytics' },
  { to: '/admin/analytics', icon: BarChart3, label: 'Analytics', perm: 'view_analytics' },
  { to: '/admin/cycles', icon: Calendar, label: 'Submission Cycles', perm: 'manage_cycles' },
  { to: '/admin/approvals', icon: ClipboardCheck, label: 'Student Approvals', perm: 'approve_students' },
  { to: '/admin/verification', icon: BadgeCheck, label: 'Verification', perm: 'approve_students' },
  { to: '/admin/flags', icon: Flag, label: 'Integrity Flags', perm: 'approve_students' },
  { to: '/admin/opportunities', icon: Megaphone, label: 'Opportunities', perm: 'view_analytics' },
  { to: '/admin/scoring', icon: SlidersHorizontal, label: 'Scoring Weights', perm: 'view_analytics' },
  { to: '/admin/reports', icon: FileBarChart, label: 'Reports', perm: 'view_analytics' },
  { to: '/admin/moderation', icon: ShieldBan, label: 'Moderation', perm: 'view_analytics' },
  { to: '/admin/team', icon: UserCog, label: 'Team', perm: 'manage_team' },
  { to: '/admin/classroom', icon: FlaskConical, label: 'Classroom Review', perm: 'manage_team' },
  { to: '/admin/student-cleanup', icon: FlaskConical, label: 'Student Cleanup', perm: 'manage_team' },
  { to: '/admin/test-accounts', icon: FlaskConical, label: 'Test Accounts', perm: 'manage_team' },
  { to: '/admin/site', icon: LayoutTemplate, label: 'Website', perm: 'manage_site' },
  { to: '/admin/settings', icon: SettingsIcon, label: 'Settings', perm: 'view_analytics' },
  { to: '/admin/profile', icon: UserCircle, label: 'My Profile' },
];

function SidebarNav({ links, pending, onNavigate }) {
  return (
    <>
      <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto scrollbar-thin">
        {links.map((l) => {
          const locked = pending && l.write;
          return (
            <NavLink
              key={l.to}
              to={locked ? '/admin' : l.to}
              end={l.end}
              onClick={(e) => {
                if (locked) e.preventDefault();
                else onNavigate?.();
              }}
              title={locked ? 'Locked — waiting for Super Admin approval' : undefined}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-colors ${
                  locked
                    ? 'text-cream/30 cursor-not-allowed'
                    : isActive
                    ? 'bg-gold-400/15 text-gold-300'
                    : 'text-cream/70 hover:bg-cream/5 hover:text-white'
                }`
              }
            >
              <l.icon className="w-4 h-4 shrink-0" /> {l.label}
              {locked && <Lock className="w-3 h-3 ml-auto" />}
            </NavLink>
          );
        })}
      </nav>
      <NavLink
        to="/"
        onClick={onNavigate}
        className="m-3 mt-0 text-xs text-cream/50 hover:text-white text-center py-2 border border-dashed border-cream/15 rounded-lg"
      >
        ← Back to public site
      </NavLink>
    </>
  );
}

export function Sidebar({ mobileOpen = false, onClose }) {
  const { role, user, can } = useAuth();
  const pending =
    SCHOOL_ADMIN_ROLES.includes(role) &&
    user?.school_approval_status &&
    user.school_approval_status !== 'approved';

  const links = LINKS.filter((l) => !l.perm || can(l.perm));

  return (
    <>
      {/* Desktop rail */}
      <aside className="hidden lg:flex flex-col w-60 shrink-0 border-r border-cream/10 bg-ink-900/70 sticky top-0 h-screen">
        <div className="px-5 h-16 flex items-center border-b border-cream/10">
          <Logo to="/admin" />
        </div>
        <SidebarNav links={links} pending={pending} />
      </aside>

      {/* Mobile drawer */}
      <AnimatePresence>
        {mobileOpen && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.15 }}
            className="lg:hidden fixed inset-0 z-50"
          >
            <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" onClick={onClose} />
            <motion.aside
              initial={{ x: '-100%' }}
              animate={{ x: 0 }}
              exit={{ x: '-100%' }}
              transition={{ type: 'tween', duration: 0.2 }}
              className="absolute left-0 top-0 h-full w-64 max-w-[80%] flex flex-col border-r border-cream/10 bg-ink-900 shadow-2xl"
            >
              <div className="px-5 h-16 flex items-center justify-between border-b border-cream/10">
                <Logo to="/admin" />
                <button onClick={onClose} className="btn-ghost h-9 w-9 p-0" aria-label="Close menu">
                  <X className="w-5 h-5" />
                </button>
              </div>
              <SidebarNav links={links} pending={pending} onNavigate={onClose} />
            </motion.aside>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}
