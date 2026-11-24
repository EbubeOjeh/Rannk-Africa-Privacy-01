import { Mail, Linkedin, MessageCircle } from 'lucide-react';

/**
 * Multi-channel contact buttons for an unlocked candidate (PRS §16).
 * Renders a button only for the channels that actually have a value, so a
 * candidate with just an email shows a single Email button.
 *
 *  - WhatsApp  → https://wa.me/<digits>  (E.164-ish, country code, no '+')
 *  - Email     → mailto:
 *  - LinkedIn  → the stored URL (normalised to include a scheme)
 */

// Best-effort normalisation of a phone number into a wa.me-friendly form.
// Strategy (kept deliberately simple/robust):
//   1. strip every non-digit (also drops a leading '+').
//   2. if it already starts with a country code (e.g. 234…), keep as-is.
//   3. if it looks like a local Nigerian number (leading 0, ~11 digits),
//      drop the 0 and prepend 234.
//   4. otherwise return the bare digits and let WhatsApp resolve them.
function toWhatsAppDigits(raw) {
  if (!raw) return '';
  let digits = String(raw).replace(/\D/g, '');
  if (!digits) return '';
  if (digits.startsWith('234')) return digits;
  if (digits.startsWith('0')) return `234${digits.replace(/^0+/, '')}`;
  return digits;
}

// Make sure a LinkedIn value is an absolute URL (users often paste it bare).
function toUrl(raw) {
  if (!raw) return '';
  const v = String(raw).trim();
  return /^https?:\/\//i.test(v) ? v : `https://${v}`;
}

export function ContactLinks({ email, whatsapp_number, linkedin_url, className = '' }) {
  const wa = toWhatsAppDigits(whatsapp_number);
  const li = toUrl(linkedin_url);

  if (!email && !wa && !li) return null;

  return (
    <div className={`flex flex-wrap items-center gap-2 ${className}`}>
      {wa && (
        <a
          href={`https://wa.me/${wa}`}
          target="_blank"
          rel="noopener noreferrer"
          className="btn-ghost text-xs"
          title="Message on WhatsApp"
        >
          <MessageCircle className="w-3.5 h-3.5 text-emerald-400" /> WhatsApp
        </a>
      )}
      {email && (
        <a href={`mailto:${email}`} className="btn-ghost text-xs" title={`Email ${email}`}>
          <Mail className="w-3.5 h-3.5 text-gold-400" /> Email
        </a>
      )}
      {li && (
        <a
          href={li}
          target="_blank"
          rel="noopener noreferrer"
          className="btn-ghost text-xs"
          title="View LinkedIn profile"
        >
          <Linkedin className="w-3.5 h-3.5 text-sky-400" /> LinkedIn
        </a>
      )}
    </div>
  );
}
