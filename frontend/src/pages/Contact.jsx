import { Mail, Instagram, Linkedin, MapPin } from 'lucide-react';
import { EditableSection } from '@/components/EditableSection';
import { BackLink } from '@/components/BackLink';
import { PageGuide } from '@/components/PageGuide';
import { usePageContent } from '@/hooks/usePageContent';

/** X (Twitter) glyph — lucide ships the old bird, so we use the official mark. */
function XIcon({ className = 'w-4 h-4' }) {
  return (
    <svg viewBox="0 0 24 24" className={className} fill="currentColor" aria-hidden="true">
      <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24h-6.66l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z" />
    </svg>
  );
}

export default function Contact() {
  const c = usePageContent('contact');
  return (
    <div className="container-page py-16 max-w-3xl">
      <BackLink className="mb-5" />
      <PageGuide
        id="contact"
        className="mb-6"
        title="Getting in touch"
        steps={[
          'Students: for problems with your profile or score, include the email you registered with.',
          'Recruiters: request access from the Sign in menu — that route is faster than email.',
          'Partnerships and media enquiries are welcome at the address below.',
        ]}
      />
      <EditableSection page="contact" id="header" title="Header">
        <p className="text-xs uppercase tracking-wider text-gold-400">{c.header.eyebrow}</p>
        <h1 className="font-display text-3xl sm:text-4xl font-extrabold mt-2">{c.header.heading}</h1>
        <p className="text-cream/70 mt-4">{c.header.intro}</p>
      </EditableSection>

      <EditableSection page="contact" id="details" title="Contact details">
        <div className="mt-8 grid sm:grid-cols-2 gap-4">
          <a
            href={`mailto:${c.email}`}
            className="card p-6 flex items-center gap-4 hover:border-gold-400/40 transition-colors group"
          >
            <span className="w-11 h-11 shrink-0 rounded-xl bg-gold-400/15 grid place-content-center text-gold-400 group-hover:bg-gold-400/25 transition-colors">
              <Mail className="w-5 h-5" />
            </span>
            <span className="min-w-0">
              <span className="block text-xs uppercase tracking-wider text-cream/40">Email</span>
              <span className="block font-semibold text-white truncate">{c.email}</span>
            </span>
          </a>

          <div className="card p-6 flex items-center gap-4">
            <span className="w-11 h-11 shrink-0 rounded-xl bg-gold-400/15 grid place-content-center text-gold-400">
              <MapPin className="w-5 h-5" />
            </span>
            <span className="min-w-0">
              <span className="block text-xs uppercase tracking-wider text-cream/40">Based in</span>
              <span className="block font-semibold text-white">{c.basedIn}</span>
            </span>
          </div>
        </div>
      </EditableSection>

      <EditableSection page="contact" id="socials" title="Social links">
        <h2 className="mt-10 font-display text-xl font-bold">{c.followHeading}</h2>
        <div className="mt-4 flex items-center gap-3">
          <a
            href={c.socials.instagram}
            target="_blank"
            rel="noopener noreferrer"
            aria-label="RankAfrica on Instagram"
            className="w-11 h-11 rounded-xl border border-cream/10 grid place-content-center text-cream/70 hover:text-white hover:border-gold-400/40 hover:bg-gold-400/10 transition-colors"
          >
            <Instagram className="w-5 h-5" />
          </a>
          <a
            href={c.socials.linkedin}
            target="_blank"
            rel="noopener noreferrer"
            aria-label="RankAfrica on LinkedIn"
            className="w-11 h-11 rounded-xl border border-cream/10 grid place-content-center text-cream/70 hover:text-white hover:border-gold-400/40 hover:bg-gold-400/10 transition-colors"
          >
            <Linkedin className="w-5 h-5" />
          </a>
          <a
            href={c.socials.x}
            target="_blank"
            rel="noopener noreferrer"
            aria-label="RankAfrica on X"
            className="w-11 h-11 rounded-xl border border-cream/10 grid place-content-center text-cream/70 hover:text-white hover:border-gold-400/40 hover:bg-gold-400/10 transition-colors"
          >
            <XIcon className="w-5 h-5" />
          </a>
        </div>

        <p className="text-xs text-cream/40 mt-10">{c.footer}</p>
      </EditableSection>
    </div>
  );
}
