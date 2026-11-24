import { Link } from 'react-router-dom';
import { Instagram, Linkedin, Mail } from 'lucide-react';
import { Logo } from './Logo';

const SOCIALS = {
  x: 'https://x.com/rankafricahq?s=11',
  instagram:
    'https://www.instagram.com/officialrankafrica?igsh=MXAza2QxeDczdXU5bw%3D%3D&utm_source=qr',
  linkedin: 'https://www.linkedin.com/company/rankafrica',
};

// Explore links point at real, standalone pages so they work from anywhere on
// the site (previously they were `/#section` anchors that bounced back to the
// landing page when clicked from an inner page).
const EXPLORE = [
  { to: '/rankings', label: 'Student rankings' },
  { to: '/universities', label: 'University rankings' },
  { to: '/fields', label: 'Fields' },
  { to: '/opportunities', label: 'Opportunities' },
];

const COMPANY = [
  { to: '/about', label: 'About' },
  { to: '/team', label: 'Team' },
  { to: '/contact', label: 'Contact' },
];

const JOIN = [
  { to: '/student-register', label: 'Create a student profile' },
  { to: '/recruiter-register', label: 'Recruiter access' },
  { to: '/login', label: 'Sign in' },
];

function LinkColumn({ heading, links }) {
  return (
    <div>
      <h4 className="text-xs font-semibold uppercase tracking-wider text-cream/40">{heading}</h4>
      <ul className="mt-3 space-y-2">
        {links.map((s) => (
          <li key={s.to}>
            <Link
              to={s.to}
              className="text-sm text-cream/70 hover:text-gold-300 transition-colors"
            >
              {s.label}
            </Link>
          </li>
        ))}
      </ul>
    </div>
  );
}

/** X (Twitter) glyph — lucide ships the old bird, so we use the official mark. */
function XIcon({ className = 'w-4 h-4' }) {
  return (
    <svg viewBox="0 0 24 24" className={className} fill="currentColor" aria-hidden="true">
      <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24h-6.66l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z" />
    </svg>
  );
}

export function Footer() {
  return (
    <footer className="border-t border-cream/10 mt-20 bg-ink-950/40">
      <div className="container-page py-12 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-10">
        <div>
          <Logo />
          <p className="text-sm text-cream/60 mt-4 max-w-xs">
            Connecting Africa's brightest students with opportunities, recognition, and career
            growth.
          </p>
          <div className="flex items-center gap-3 mt-5">
            <a
              href={SOCIALS.instagram}
              target="_blank"
              rel="noopener noreferrer"
              aria-label="RankAfrica on Instagram"
              className="w-9 h-9 rounded-lg border border-cream/10 grid place-content-center text-cream/70 hover:text-white hover:border-gold-400/40 transition-colors"
            >
              <Instagram className="w-4 h-4" />
            </a>
            <a
              href={SOCIALS.linkedin}
              target="_blank"
              rel="noopener noreferrer"
              aria-label="RankAfrica on LinkedIn"
              className="w-9 h-9 rounded-lg border border-cream/10 grid place-content-center text-cream/70 hover:text-white hover:border-gold-400/40 transition-colors"
            >
              <Linkedin className="w-4 h-4" />
            </a>
            <a
              href={SOCIALS.x}
              target="_blank"
              rel="noopener noreferrer"
              aria-label="RankAfrica on X"
              className="w-9 h-9 rounded-lg border border-cream/10 grid place-content-center text-cream/70 hover:text-white hover:border-gold-400/40 transition-colors"
            >
              <XIcon />
            </a>
          </div>
        </div>

        <LinkColumn heading="Explore" links={EXPLORE} />

        <div>
          <LinkColumn heading="Company" links={COMPANY} />
          <a
            href="mailto:info@rankafrica.org"
            className="mt-3 inline-flex items-center gap-2 text-sm text-cream/70 hover:text-gold-300"
          >
            <Mail className="w-4 h-4" /> info@rankafrica.org
          </a>
        </div>

        <LinkColumn heading="Get started" links={JOIN} />
      </div>

      <div className="border-t border-cream/10">
        <div className="container-page py-5 flex flex-col sm:flex-row items-center justify-between gap-2">
          <p className="text-xs text-cream/50">© 2026 Rank Africa</p>
          <p className="text-xs text-cream/40">Ranking Student Excellence</p>
        </div>
      </div>
    </footer>
  );
}
