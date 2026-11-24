import { useState, useEffect, useRef } from 'react';
import { Link, NavLink, useLocation } from 'react-router-dom';
import { ChevronDown, LogIn, LogOut, Menu, X, UserPlus } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { Logo } from './Logo';
import { useAuth } from '@/hooks/useAuth';
import { useLogout } from '@/hooks/useLogout';
import { ACCOUNT_TYPE_LIST } from '@/utils/accountTypes';

/**
 * The primary public navigation, shown on every platform page (including the
 * home page). Rankings comes first deliberately: it is the product, and until
 * this existed the leaderboard was reachable only by typing the URL.
 *
 * About / Team / Contact are low-frequency trust pages and live in the footer
 * instead, so the bar stays scannable on a phone.
 */
const PLATFORM_NAV = [
  { to: '/rankings', label: 'Rankings' },
  { to: '/fields', label: 'Fields' },
  { to: '/universities', label: 'Universities' },
  { to: '/opportunities', label: 'Opportunities' },
  { to: '/about', label: 'About' },
];

// The two public audiences, for the "Join" menu. Staff have no register link.
const REGISTER_LINKS = ACCOUNT_TYPE_LIST.filter((t) => t.register);

/**
 * Shared top bar.
 *  - `showNav`: the primary navigation. Auth pages turn it off.
 *  - `showLogin`: the sign-in / join controls. Auth pages turn these off too.
 */
export function Navbar({ showNav = true, showLogin = true }) {
  const { isAuthenticated, user } = useAuth();
  const logout = useLogout();
  const [openMobile, setOpenMobile] = useState(false);
  const [openLogin, setOpenLogin] = useState(false);
  const location = useLocation();
  const loginRef = useRef(null);

  useEffect(() => {
    setOpenMobile(false);
    setOpenLogin(false);
  }, [location.pathname]);

  useEffect(() => {
    const handler = (e) => {
      if (loginRef.current && !loginRef.current.contains(e.target)) setOpenLogin(false);
    };
    window.addEventListener('mousedown', handler);
    return () => window.removeEventListener('mousedown', handler);
  }, []);

  // Lock body scroll while the mobile drawer is open, so the page behind it
  // doesn't scroll under the user's finger.
  useEffect(() => {
    document.body.style.overflow = openMobile ? 'hidden' : '';
    return () => {
      document.body.style.overflow = '';
    };
  }, [openMobile]);

  const linkClass = 'text-sm text-white/80 hover:text-white transition-colors';
  const navLinkClass = ({ isActive }) =>
    isActive ? 'text-sm font-semibold text-gold-400' : linkClass;

  // Auth pages turn both off, so they get no hamburger either.
  const navLinks = PLATFORM_NAV;
  const hasMobileMenu = showNav || showLogin;

  const authControls = isAuthenticated ? (
    <div className="flex items-center gap-2">
      <Link to="/admin" className="btn-primary text-xs">
        {user?.name?.split(' ')[0] || 'Dashboard'}
      </Link>
      <button onClick={logout} className="btn-ghost text-xs" title="Log out">
        <LogOut className="w-4 h-4" />
      </button>
    </div>
  ) : (
    <div className="flex items-center gap-2">
      {/* Registration was previously unreachable from any public page. */}
      <Link to="/student-register" className="btn-primary text-xs hidden lg:inline-flex">
        <UserPlus className="w-4 h-4" /> Join
      </Link>
      <div className="relative" ref={loginRef}>
        <button
          onClick={() => setOpenLogin((v) => !v)}
          className="btn-ghost text-xs"
          aria-haspopup="menu"
          aria-expanded={openLogin}
        >
          <LogIn className="w-4 h-4" /> Sign in <ChevronDown className="w-3.5 h-3.5" />
        </button>
        <AnimatePresence>
          {openLogin && (
            <motion.div
              initial={{ opacity: 0, y: 6 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: 6 }}
              transition={{ duration: 0.15 }}
              role="menu"
              className="absolute right-0 mt-2 w-64 rounded-xl bg-ink-850 border border-white/5 shadow-xl overflow-hidden"
            >
              <p className="px-4 pt-3 pb-1 text-[11px] uppercase tracking-wider text-cream/40">
                New here?
              </p>
              {REGISTER_LINKS.map((t) => (
                <Link
                  key={t.register.to}
                  to={t.register.to}
                  className="flex items-center gap-3 px-4 py-2.5 text-sm text-white/80 hover:bg-white/5 hover:text-white"
                >
                  <t.icon className="w-4 h-4 text-gold-400" />
                  {t.register.label}
                </Link>
              ))}
              <div className="border-t border-white/5 my-1" />
              <p className="px-4 pt-2 pb-1 text-[11px] uppercase tracking-wider text-cream/40">
                Sign in as
              </p>
              {ACCOUNT_TYPE_LIST.map((t) => (
                <div key={t.key}>
                  {t.key === 'employee' && <div className="border-t border-white/5 my-1" />}
                  <Link
                    to={`/login?as=${t.key}`}
                    className="flex items-center gap-3 px-4 py-2.5 text-sm text-white/80 hover:bg-white/5 hover:text-white"
                  >
                    <t.icon className="w-4 h-4 text-gold-400" />
                    {t.label}
                  </Link>
                </div>
              ))}
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );

  return (
    <header className="sticky top-0 z-40 bg-ink-950/80 backdrop-blur-md border-b border-white/5">
      <div className="container-page flex items-center justify-between h-16 gap-4">
        <Logo />

        <nav className="hidden md:flex items-center gap-6 lg:gap-7">
          {showNav &&
            navLinks.map((s) => (
              <NavLink key={s.to} to={s.to} className={navLinkClass}>
                {s.label}
              </NavLink>
            ))}
          {showLogin && authControls}
        </nav>

        {hasMobileMenu && (
          <button
            className="md:hidden btn-ghost h-11 w-11 p-0"
            onClick={() => setOpenMobile((v) => !v)}
            aria-label={openMobile ? 'Close menu' : 'Open menu'}
            aria-expanded={openMobile}
          >
            {openMobile ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </button>
        )}
      </div>

      <AnimatePresence>
        {openMobile && hasMobileMenu && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            className="md:hidden overflow-hidden border-t border-white/5 bg-ink-950/95 max-h-[calc(100vh-4rem)] overflow-y-auto"
          >
            <div className="container-page py-2 flex flex-col">
              {showNav &&
                navLinks.map((s) => (
                  <NavLink
                    key={s.to}
                    to={s.to}
                    onClick={() => setOpenMobile(false)}
                    className={({ isActive }) =>
                      `block py-3.5 text-base border-b border-white/5 ${
                        isActive ? 'text-gold-400 font-semibold' : 'text-white/85'
                      }`
                    }
                  >
                    {s.label}
                  </NavLink>
                ))}

              {showLogin &&
                (isAuthenticated ? (
                  <div className="flex items-center gap-2 py-3">
                    <Link to="/admin" className="btn-primary text-sm">
                      {user?.name?.split(' ')[0] || 'Dashboard'}
                    </Link>
                    <button onClick={logout} className="btn-ghost text-sm">
                      <LogOut className="w-4 h-4" /> Log out
                    </button>
                  </div>
                ) : (
                  <div className="py-3">
                    <p className="text-[11px] uppercase tracking-wider text-cream/40 mb-1">
                      New here?
                    </p>
                    {REGISTER_LINKS.map((t) => (
                      <Link
                        key={t.register.to}
                        to={t.register.to}
                        className="flex items-center gap-3 py-3 text-base text-white/85"
                        onClick={() => setOpenMobile(false)}
                      >
                        <t.icon className="w-4 h-4 text-gold-400" />
                        {t.register.label}
                      </Link>
                    ))}
                    <div className="border-t border-white/5 my-1" />
                    <p className="text-[11px] uppercase tracking-wider text-cream/40 mt-2 mb-1">
                      Sign in as
                    </p>
                    {ACCOUNT_TYPE_LIST.map((t) => (
                      <Link
                        key={t.key}
                        to={`/login?as=${t.key}`}
                        className="flex items-center gap-3 py-3 text-base text-white/85"
                        onClick={() => setOpenMobile(false)}
                      >
                        <t.icon className="w-4 h-4 text-gold-400" />
                        {t.label}
                      </Link>
                    ))}
                  </div>
                ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </header>
  );
}
