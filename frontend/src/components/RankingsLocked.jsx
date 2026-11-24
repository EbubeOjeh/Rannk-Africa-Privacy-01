import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';
import { Lock, ArrowRight } from 'lucide-react';

/**
 * Shown on the public ranking surfaces while rankings are hidden (registration
 * open). Keeps a single, consistent "coming soon" message across pages, and
 * offers a way onward — it used to be a dead end.
 */
export function RankingsLocked({ message }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      className="mt-8 card p-10 sm:p-14 text-center max-w-2xl mx-auto"
    >
      <div className="w-14 h-14 mx-auto rounded-2xl bg-gold-400/15 grid place-content-center text-gold-400">
        <Lock className="w-6 h-6" />
      </div>
      <h2 className="mt-5 font-display text-2xl font-bold">Rankings are on the way</h2>
      <p className="mt-3 text-cream/70 leading-relaxed">{message}</p>
      <p className="mt-6 text-xs uppercase tracking-wider text-gold-400">
        Registration is open now
      </p>
      <div className="mt-6 flex flex-col sm:flex-row gap-3 justify-center">
        <Link to="/student-register" className="btn-primary">
          Create your student profile <ArrowRight className="w-4 h-4" />
        </Link>
        <Link to="/fields" className="btn-outline">
          Browse disciplines
        </Link>
      </div>
    </motion.div>
  );
}
