import { useState } from 'react';
import { Link } from 'react-router-dom';
import { AnimatePresence, motion } from 'framer-motion';
import { HelpCircle, X, ChevronDown } from 'lucide-react';

const STORAGE_PREFIX = 'ra:guide:';

const dismissed = (id) => {
  try {
    return localStorage.getItem(STORAGE_PREFIX + id) === '1';
  } catch {
    return false;
  }
};

const remember = (id) => {
  try {
    localStorage.setItem(STORAGE_PREFIX + id, '1');
  } catch {
    /* private mode — the guide just reappears next visit */
  }
};

/**
 * The short "what is this page and what can I do here" panel that sits at the
 * top of every public and signed-in surface.
 *
 * It is open the first time someone lands on a page and collapses to a single
 * "What can I do here?" line once dismissed, remembered per page in
 * localStorage — so it teaches new visitors without nagging returning ones.
 * Collapsing rather than disappearing matters: a visitor who dismissed it and
 * is later confused still has somewhere to look.
 *
 * @param id     stable key for the dismissal memory (one per page)
 * @param title  what this page is
 * @param steps  the actions available here, in the order they make sense
 * @param cta    optional {to, label} primary next step
 */
export function PageGuide({ id, title, steps = [], cta, className = '' }) {
  const [open, setOpen] = useState(() => !dismissed(id));

  const close = () => {
    setOpen(false);
    remember(id);
  };

  return (
    <div className={className}>
      <AnimatePresence initial={false}>
        {open ? (
          <motion.div
            key="open"
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="overflow-hidden"
          >
            <div className="card p-5 border-gold-400/20 bg-gold-400/[0.04]">
              <div className="flex items-start gap-3">
                <span className="w-8 h-8 shrink-0 rounded-lg bg-gold-400/15 grid place-content-center text-gold-400">
                  <HelpCircle className="w-4 h-4" />
                </span>
                <div className="min-w-0 flex-1">
                  <p className="font-semibold text-white">{title}</p>
                  <ul className="mt-3 space-y-2">
                    {steps.map((s, i) => (
                      <li key={i} className="flex gap-3 text-sm text-cream/75">
                        <span className="shrink-0 w-5 h-5 rounded-full bg-cream/10 text-[11px] font-semibold grid place-content-center text-cream/70">
                          {i + 1}
                        </span>
                        <span className="leading-relaxed">{s}</span>
                      </li>
                    ))}
                  </ul>
                  {cta && (
                    <Link to={cta.to} className="btn-primary text-xs mt-4">
                      {cta.label}
                    </Link>
                  )}
                </div>
                <button
                  type="button"
                  onClick={close}
                  aria-label="Hide guide"
                  className="shrink-0 w-8 h-8 grid place-content-center rounded-lg text-cream/50 hover:text-white hover:bg-cream/5"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
            </div>
          </motion.div>
        ) : (
          <motion.button
            key="closed"
            type="button"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            onClick={() => setOpen(true)}
            className="inline-flex items-center gap-2 text-sm text-cream/55 hover:text-gold-300 transition-colors"
          >
            <HelpCircle className="w-4 h-4" />
            What can I do here?
            <ChevronDown className="w-3.5 h-3.5" />
          </motion.button>
        )}
      </AnimatePresence>
    </div>
  );
}
