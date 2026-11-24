import { motion, AnimatePresence } from 'framer-motion';
import { CheckCircle2, Instagram } from 'lucide-react';

export const INSTAGRAM_HANDLE = 'OfficialRankAfrica';
export const INSTAGRAM_URL = `https://instagram.com/${INSTAGRAM_HANDLE}`;

/**
 * Centred confirmation dialog used at the two milestones of the student sign-up
 * journey: account created (StudentRegister) and every section completed
 * (ProfileBuilder).
 *
 *  - `children` is the body copy.
 *  - `social` appends the Instagram link under the body.
 *  - `note` is an optional smaller line under that.
 *
 * There is no dismiss-on-backdrop-click: the CTA is the only way out, because
 * closing navigates the student onward.
 */
export function SuccessModal({ open, title, children, cta = 'Continue', onClose, social = true, note }) {
  return (
    <AnimatePresence>
      {open && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          role="dialog"
          aria-modal="true"
          aria-label={title}
          className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm"
        >
          <motion.div
            initial={{ opacity: 0, scale: 0.94, y: 12 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.94, y: 12 }}
            transition={{ duration: 0.2 }}
            className="card w-full max-w-md p-7 text-center"
          >
            <div className="w-12 h-12 mx-auto rounded-xl bg-gold-400/15 grid place-content-center text-gold-400">
              <CheckCircle2 className="w-6 h-6" />
            </div>
            <h2 className="mt-4 font-display text-xl font-bold">{title}</h2>
            <p className="mt-3 text-sm text-cream/75 leading-relaxed">{children}</p>

            {social && (
              <a
                href={INSTAGRAM_URL}
                target="_blank"
                rel="noreferrer"
                className="mt-4 inline-flex items-center gap-2 text-sm text-gold-300 hover:underline"
              >
                <Instagram className="w-4 h-4" />@{INSTAGRAM_HANDLE}
              </a>
            )}

            {note && <p className="mt-3 text-xs text-cream/55 leading-relaxed">{note}</p>}

            <button onClick={onClose} className="btn-primary mt-6 w-full justify-center">
              {cta}
            </button>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
