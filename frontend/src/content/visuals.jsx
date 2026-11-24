/**
 * Shared visual vocabulary for the dynamic landing page.
 *
 * Content stored in the DB references icons and accent colours by *name*
 * (plain strings), never by component reference — so the CEO/admin can pick
 * them from the dashboard without touching code. This module maps those names
 * to real lucide icons and Tailwind class sets.
 *
 * IMPORTANT: the accent class strings below are written out in full (no string
 * concatenation) so Tailwind's content scanner keeps them in the build. Add a
 * new accent here and it is instantly available in the editor.
 */
import {
  Scale,
  Cpu,
  Stethoscope,
  HardHat,
  Building2,
  Building,
  Landmark,
  Music,
  Briefcase,
  Newspaper,
  GraduationCap,
  Trophy,
  TrendingUp,
  Instagram,
  Linkedin,
  Mail,
  Sparkles,
  BookOpen,
  Globe,
  Award,
  Users,
  Lightbulb,
  Rocket,
  Heart,
  Star,
  Palette,
  Camera,
  Code,
  Microscope,
  Megaphone,
  Compass,
  Target,
  Gem,
  Flag,
  Calendar,
  Shield,
  Wallet,
  Beaker,
  Atom,
  Gavel,
  PenTool,
  Wrench,
} from 'lucide-react';

/** X (Twitter) glyph — lucide ships the old bird, so we use the official mark. */
export function XIcon({ className = 'w-5 h-5' }) {
  return (
    <svg viewBox="0 0 24 24" className={className} fill="currentColor" aria-hidden="true">
      <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24h-6.66l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z" />
    </svg>
  );
}

/** name -> icon component. The editor's icon picker is built from the keys. */
export const ICONS = {
  Scale,
  Cpu,
  Stethoscope,
  HardHat,
  Building2,
  Building,
  Landmark,
  Music,
  Briefcase,
  Newspaper,
  GraduationCap,
  Trophy,
  TrendingUp,
  Instagram,
  Linkedin,
  Mail,
  Sparkles,
  BookOpen,
  Globe,
  Award,
  Users,
  Lightbulb,
  Rocket,
  Heart,
  Star,
  Palette,
  Camera,
  Code,
  Microscope,
  Megaphone,
  Compass,
  Target,
  Gem,
  Flag,
  Calendar,
  Shield,
  Wallet,
  Beaker,
  Atom,
  Gavel,
  PenTool,
  Wrench,
  X: XIcon,
};

/** Ordered list of icon names for the picker UI. */
export const ICON_NAMES = Object.keys(ICONS);

/** Resolve an icon name to a component, falling back to Sparkles. */
export function iconFor(name) {
  return ICONS[name] || Sparkles;
}

/**
 * name -> Tailwind class set for a card's accent. Full literal strings only
 * (see file header). Each card stores its accent name; the page applies these.
 */
export const ACCENTS = {
  gold: {
    label: 'Gold',
    swatch: 'bg-gold-400',
    chipBg: 'bg-gold-400/15',
    chipText: 'text-gold-400',
    chipHover: 'group-hover:bg-gold-400/25',
    border: 'hover:border-gold-400/40',
    note: 'group-hover:text-gold-300',
  },
  forest: {
    label: 'Forest',
    swatch: 'bg-forest-400',
    chipBg: 'bg-forest-400/20',
    chipText: 'text-forest-300',
    chipHover: 'group-hover:bg-forest-400/30',
    border: 'hover:border-forest-400/40',
    note: 'group-hover:text-forest-200',
  },
  emerald: {
    label: 'Emerald',
    swatch: 'bg-emerald-400',
    chipBg: 'bg-emerald-400/15',
    chipText: 'text-emerald-300',
    chipHover: 'group-hover:bg-emerald-400/25',
    border: 'hover:border-emerald-400/40',
    note: 'group-hover:text-emerald-200',
  },
  sky: {
    label: 'Sky',
    swatch: 'bg-sky-400',
    chipBg: 'bg-sky-400/15',
    chipText: 'text-sky-300',
    chipHover: 'group-hover:bg-sky-400/25',
    border: 'hover:border-sky-400/40',
    note: 'group-hover:text-sky-200',
  },
  violet: {
    label: 'Violet',
    swatch: 'bg-violet-400',
    chipBg: 'bg-violet-400/15',
    chipText: 'text-violet-300',
    chipHover: 'group-hover:bg-violet-400/25',
    border: 'hover:border-violet-400/40',
    note: 'group-hover:text-violet-200',
  },
  rose: {
    label: 'Rose',
    swatch: 'bg-rose-400',
    chipBg: 'bg-rose-400/15',
    chipText: 'text-rose-300',
    chipHover: 'group-hover:bg-rose-400/25',
    border: 'hover:border-rose-400/40',
    note: 'group-hover:text-rose-200',
  },
  amber: {
    label: 'Amber',
    swatch: 'bg-amber-400',
    chipBg: 'bg-amber-400/15',
    chipText: 'text-amber-300',
    chipHover: 'group-hover:bg-amber-400/25',
    border: 'hover:border-amber-400/40',
    note: 'group-hover:text-amber-200',
  },
};

export const ACCENT_NAMES = Object.keys(ACCENTS);

/** Resolve an accent name to its class set, falling back to gold. */
export function accentFor(name) {
  return ACCENTS[name] || ACCENTS.gold;
}
