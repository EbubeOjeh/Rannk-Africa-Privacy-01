import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Navbar } from './Navbar';

/**
 * Shared shell for every authentication page (login, school register,
 * recruiter register) so they stay visually uniform: same navbar, centered
 * column, dark premium background and a consistent "return home" link.
 */
export function AuthShell({ children, maxWidth = 'max-w-md' }) {
  return (
    <div className="min-h-screen bg-ink-950 flex flex-col">
      <Navbar showNav={false} showLogin={false} />
      <main className="flex-1 flex items-center justify-center px-4 py-12">
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4 }}
          className={`w-full ${maxWidth}`}
        >
          {children}
          <p className="text-center text-xs text-cream/40 mt-6">
            <Link to="/" className="hover:text-cream/70 transition-colors">
              ← Return to homepage
            </Link>
          </p>
        </motion.div>
      </main>
    </div>
  );
}

/** Consistent gold-badge header used at the top of every auth card. */
export function AuthHeader({ icon: Icon, title, subtitle }) {
  return (
    <div className="text-center mb-6">
      <div className="w-12 h-12 mx-auto rounded-xl bg-gold-400/15 grid place-content-center text-gold-400">
        <Icon className="w-6 h-6" />
      </div>
      <h1 className="font-display text-2xl font-bold mt-3">{title}</h1>
      {subtitle && <p className="text-sm text-cream/60 mt-1 max-w-sm mx-auto">{subtitle}</p>}
    </div>
  );
}
