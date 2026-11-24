import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { ArrowRight } from 'lucide-react';

/**
 * Live, data-driven strips for the landing page, lifted out of the retired
 * launching-soon page (there is one landing page now). Both are
 * purely additive: each returns null when its data is empty or the request
 * failed, so the page never shows an empty shell.
 */
const fadeUp = {
  initial: { opacity: 0, y: 20 },
  whileInView: { opacity: 1, y: 0 },
  viewport: { once: true, margin: '-80px' },
  transition: { duration: 0.6 },
};

export function LatestOpportunities({ items }) {
  const list = (items || []).filter(Boolean);
  if (list.length === 0) return null;

  return (
    <section className="container-page mt-16">
      <motion.div {...fadeUp} className="flex items-end justify-between gap-4">
        <div>
          <h2 className="font-display text-2xl font-bold">Latest opportunities</h2>
          <p className="text-cream/60 mt-1 text-sm">
            Fresh roles, scholarships and competitions open to ranked students.
          </p>
        </div>
        <Link to="/opportunities" className="btn-outline text-xs shrink-0">
          View all <ArrowRight className="w-3.5 h-3.5" />
        </Link>
      </motion.div>

      <motion.ul {...fadeUp} className="mt-6 card divide-y divide-cream/5">
        {list.map((o, i) => (
          <li key={o.id || i}>
            <Link
              to="/opportunities"
              className="flex items-center justify-between gap-3 px-5 py-4 hover:bg-cream/[0.03] transition-colors"
            >
              <div className="min-w-0">
                <p className="font-medium text-white truncate">{o.title}</p>
                {o.organization && (
                  <p className="text-xs text-cream/50 mt-0.5 truncate">{o.organization}</p>
                )}
              </div>
              <div className="flex items-center gap-3 shrink-0">
                {o.type && (
                  <span className="tag bg-gold-400/[0.08] text-gold-300 capitalize hidden sm:inline-flex">
                    {o.type}
                  </span>
                )}
                <ArrowRight className="w-4 h-4 text-cream/40" />
              </div>
            </Link>
          </li>
        ))}
      </motion.ul>
    </section>
  );
}

export function FeaturedEmployers({ employers }) {
  const list = (employers || []).filter(Boolean);
  if (list.length === 0) return null;

  return (
    <section className="container-page mt-16">
      <motion.div {...fadeUp}>
        <h2 className="font-display text-2xl font-bold">Trusted by employers</h2>
        <p className="text-cream/60 mt-1 text-sm">Organisations hiring through Rank Africa.</p>
      </motion.div>
      <motion.div {...fadeUp} className="mt-6 flex flex-wrap items-center gap-3">
        {list.map((e, i) => (
          <div
            key={e.id || i}
            className="card px-4 py-3 flex items-center gap-3 min-w-0"
            title={e.company_name}
          >
            <EmployerLogo src={e.logo_url} fallback={initials(e.company_name)} />
            <span className="text-sm font-medium text-white truncate max-w-[12rem]">
              {e.company_name}
            </span>
          </div>
        ))}
      </motion.div>
    </section>
  );
}

function initials(name) {
  if (!name) return '?';
  return name
    .split(/\s+/)
    .filter(Boolean)
    .slice(0, 2)
    .map((w) => w[0]?.toUpperCase())
    .join('');
}

function EmployerLogo({ src, fallback }) {
  if (src) {
    return (
      <img
        src={src}
        alt=""
        className="w-10 h-10 rounded-xl object-cover bg-cream/5 shrink-0"
        loading="lazy"
      />
    );
  }
  return (
    <span className="w-10 h-10 rounded-xl bg-gold-400/15 text-gold-300 grid place-content-center font-bold shrink-0">
      {fallback}
    </span>
  );
}
