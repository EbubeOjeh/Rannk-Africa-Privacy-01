import { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { FileText, X } from 'lucide-react';
import { studentService } from '@/services/student.service';

/**
 * Shared Terms & Conditions surfaces used by every registration flow
 * (student, recruiter, school). Keeping them in one place means all three
 * pages render the SAME clause text and stay in sync — the copy itself is
 * served role-agnostically from the backend (`GET /auth/terms`).
 */

/** Modal that self-loads and renders the current Terms & Conditions. */
export function TermsModal({ open, onClose }) {
  const [terms, setTerms] = useState(null);

  useEffect(() => {
    if (!open || terms) return;
    studentService
      .getTerms()
      .then(setTerms)
      .catch(() =>
        setTerms({ confirmation: 'Could not load the terms. Please try again.', clauses: [] })
      );
  }, [open, terms]);

  return (
    <AnimatePresence>
      {open && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm"
          onClick={onClose}
        >
          <motion.div
            initial={{ opacity: 0, scale: 0.96, y: 8 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.96, y: 8 }}
            onClick={(e) => e.stopPropagation()}
            className="card w-full max-w-lg max-h-[80vh] flex flex-col"
          >
            <div className="flex items-center justify-between px-6 py-4 border-b border-cream/10">
              <div className="flex items-center gap-2">
                <FileText className="w-4 h-4 text-gold-400" />
                <h2 className="font-display font-bold">
                  Terms &amp; Conditions
                  {terms?.version ? (
                    <span className="text-cream/40 text-xs font-medium"> · v{terms.version}</span>
                  ) : null}
                </h2>
              </div>
              <button onClick={onClose} className="btn-ghost h-8 w-8 p-0" aria-label="Close terms">
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="px-6 py-4 overflow-y-auto scrollbar-thin space-y-3 text-sm text-cream/80">
              {!terms ? (
                <p className="text-cream/50">Loading…</p>
              ) : (
                <>
                  {terms.confirmation && <p className="text-cream/90">{terms.confirmation}</p>}
                  {Array.isArray(terms.clauses) && terms.clauses.length > 0 && (
                    <ol className="list-decimal list-inside space-y-2 text-cream/70">
                      {terms.clauses.map((c, i) => (
                        <li key={i}>{c}</li>
                      ))}
                    </ol>
                  )}
                </>
              )}
            </div>

            <div className="px-6 py-4 border-t border-cream/10">
              <button onClick={onClose} className="btn-primary w-full">
                Got it
              </button>
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}

/**
 * Required "I agree to the Terms & Conditions" checkbox + an inline modal opener.
 * The parent owns the boolean (`accepted`) so it can gate the submit button.
 *  - `extra`: optional trailing sentence appended after the T&C link.
 */
export function TermsAgreement({ accepted, onChange, extra }) {
  const [showTerms, setShowTerms] = useState(false);

  return (
    <>
      <label className="flex items-start gap-3 rounded-lg border border-cream/10 bg-ink-900/50 px-4 py-3 cursor-pointer">
        <input
          type="checkbox"
          checked={accepted}
          onChange={(e) => onChange(e.target.checked)}
          className="mt-0.5 h-4 w-4 shrink-0 accent-gold-400"
          required
        />
        <span className="text-xs text-cream/80">
          I agree to the{' '}
          <button
            type="button"
            onClick={() => setShowTerms(true)}
            className="text-gold-300 hover:underline font-medium"
          >
            Terms &amp; Conditions
          </button>
          .{extra ? ` ${extra}` : ''}
        </span>
      </label>

      <TermsModal open={showTerms} onClose={() => setShowTerms(false)} />
    </>
  );
}
