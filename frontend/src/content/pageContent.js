/**
 * Central content model for every editable public page.
 *
 * Each page renders `mergeContent(PAGE_DEFAULTS[key], savedDocument)` — so the
 * code defaults below are the single source of truth for what the live site
 * shows before anyone edits it, and the admin's saved edits are layered on top.
 * The defaults MUST mirror the current on-page copy exactly, so making a page
 * editable does not change how it looks until someone actually edits it.
 *
 * `EDIT_SCHEMA` describes the editable fields per page. The Website editor
 * renders its forms from this schema, and each page wraps its sections in
 * <EditableSection page= id=> matching a schema `section.id`, so clicking a
 * section in the live preview opens exactly that group of fields.
 *
 * The launching-soon landing page and its bespoke editor were retired at
 * launch: there is a single landing page at "/", edited under the `platform`
 * key like every other page.
 */
import { mergeContent } from '@/content/contentMerge';

export { mergeContent };

// Page key → the site_content document key it is stored under. The rankings
// PAGE copy uses `rankings_page` because `rankings` is already the
// rankings-release switch document.
export const STORAGE_KEYS = {
  platform: 'platform',
  about: 'about',
  opportunities: 'opportunities_page',
  contact: 'contact',
  rankings: 'rankings_page',
  universities: 'universities',
  fields: 'fields',
  team: 'team',
};

// Order + labels for the editor's page selector.
export const PAGES = [
  { key: 'platform', label: 'Home / Landing page', path: '/' },
  { key: 'about', label: 'About', path: '/about' },
  { key: 'opportunities', label: 'Opportunities', path: '/opportunities' },
  { key: 'rankings', label: 'Student Rankings', path: '/rankings' },
  { key: 'universities', label: 'University Rankings', path: '/universities' },
  { key: 'fields', label: 'Fields', path: '/fields' },
  { key: 'team', label: 'Team', path: '/team' },
  { key: 'contact', label: 'Contact', path: '/contact' },
];

export const PAGE_DEFAULTS = {

  platform: {
    hero: {
      eyebrow: 'Africa’s student ranking platform',
      titleLead: 'Discover Africa’s',
      titleHighlight: 'Top Students',
      subtitle:
        'Comprehensive, standardised rankings of the brightest students — academics, projects and verified achievements combined into a single transparent /100 index that universities, employers and partners can trust.',
    },
    browse: {
      heading: 'Browse by Field',
      subtitle: 'Explore rankings across tech disciplines — Phase 1 focus.',
    },
    mission: {
      eyebrow: 'Our Mission',
      heading: 'Make academic excellence visible — and rewarded',
      body: 'RankAfrica gives every student a fair, standardised score that travels — so talent is recognised on merit, wherever it comes from, and connected to real opportunity.',
    },
    vision: {
      eyebrow: 'Our Vision',
      heading: 'The trusted standard for student recognition in Africa',
      body: 'A continent-wide index that universities, employers and partners rely on to discover and back the next generation of builders, researchers and leaders.',
    },
  },

  about: {
    header: {
      eyebrow: 'About RankAfrica',
      heading: 'A Standardised Academic Performance + Innovation Index',
      intro:
        'RankAfrica is a merit-based ranking platform for African students. Every student is evaluated on a standardized 100-point scale based on the criteria for their field.',
    },
    mission: {
      title: 'Our mission',
      body: 'Make academic excellence visible — and rewarded. We give every student a fair, standardised score that travels, so talent is recognised on merit and connected to real opportunity.',
    },
    vision: {
      title: 'Our vision',
      body: 'To be the trusted standard for student recognition in Africa — relied on by universities, employers and partners to discover and back the next generation.',
    },
    pipelines: {
      heading: 'The three pipelines',
      items: [
        {
          title: 'Academic /40',
          body: '(CGPA / 4.0) × 40. Transcripts are normalised to a 4.0 scale before scoring, so a 4.5/5.0 and a 3.6/4.0 are compared on equal footing.',
        },
        {
          title: 'Project Intelligence /40',
          body: 'A constrained AI rubric evaluates the final-year project against four fixed categories — Originality, Technical Depth, Problem Solving, Innovation — each scored 0-10 with strict JSON output. Top-tier scores are reviewed by a human moderator.',
        },
        {
          title: 'Achievements /20',
          body: 'Verified achievements add points up to a /20 cap: Internship (3), Hackathon Participation (2), Hackathon Win (5), Leadership Role (5), Publication (6), Startup Built (8).',
        },
      ],
    },
    roadmap: {
      heading: 'Roadmap',
      subtitle: 'Where we are, and where we’re headed.',
      items: [
        { phase: 'Live now', title: 'The platform is running', body: 'Schools register and are verified, students are scored on the /100 index, and recruiters can request verified access.', state: 'done' },
        { phase: 'In progress', title: 'Recognition & reach', body: 'Recruiter verification, historical season archives, and richer school & student profiles.', state: 'active' },
        { phase: 'Next', title: 'Breadth & partnerships', body: 'More disciplines, wider national coverage, and integrations with partner organisations and scholarships.', state: 'next' },
        { phase: 'Q1 2027', title: 'Continent-wide launch', body: 'Public roll-out across African institutions as the trusted standard for student recognition.', state: 'next' },
      ],
    },
    teamCta: {
      heading: 'Meet the team building RankAfrica',
      body: 'The people behind the platform.',
      label: 'View the team',
    },
    footer: {
      note: 'RankAfrica is not designed to answer "Who is the smartest student?" — it builds a transparent, merit-based framework that makes African student talent legible to employers, scholarships, and opportunities worldwide.',
    },
  },

  opportunities: {
    header: {
      eyebrow: 'RankAfrica',
      heading: 'Opportunities',
      intro:
        'Internships, graduate jobs, scholarships, research, competitions and leadership programs from organisations hiring across the continent.',
    },
  },

  rankings: {
    header: {
      eyebrow: 'National Leaderboard',
      heading: 'Student Rankings',
    },
  },

  universities: {
    header: {
      eyebrow: 'Institution Rankings',
      heading: 'University Rankings',
      subtitle: 'African universities ranked by student performance and institutional weight',
    },
  },

  fields: {
    header: {
      heading: 'Browse Fields',
    },
  },

  team: {
    header: {
      eyebrow: 'Our Team',
      heading: 'The people behind RankAfrica',
      subtitle: 'A team building Africa’s most credible standard for recognising student excellence.',
      emptyNote: 'Team profiles are being added — check back shortly.',
    },
  },

  contact: {
    header: {
      eyebrow: 'Contact RankAfrica',
      heading: 'Get in touch',
      intro:
        'Questions about registering your school, recruiter access, or how the /100 ranking works? Reach out — the RankAfrica team is happy to help.',
    },
    email: 'info@rankafrica.org',
    basedIn: 'Nigeria · Serving Africa',
    followHeading: 'Follow us',
    footer: 'We typically respond within a couple of business days.',
    socials: {
      instagram:
        'https://www.instagram.com/officialrankafrica?igsh=MXAza2QxeDczdXU5bw%3D%3D&utm_source=qr',
      linkedin: 'https://www.linkedin.com/company/rankafrica',
      x: 'https://x.com/rankafricahq?s=11',
    },
  },
};

/**
 * Editable fields per page (non-landing). `id` matches the page's
 * <EditableSection id=> so the preview can jump to it. `path` is a dot-path
 * inside the page's content object. `list` renders a repeatable card group.
 */
export const EDIT_SCHEMA = {
  platform: [
    {
      id: 'hero',
      title: 'Hero',
      fields: [
        { path: 'hero.eyebrow', label: 'Eyebrow' },
        { path: 'hero.titleLead', label: 'Title — start' },
        { path: 'hero.titleHighlight', label: 'Title — highlight (gold)' },
        { path: 'hero.subtitle', label: 'Subtitle', textarea: true },
      ],
    },
    {
      id: 'browse',
      title: 'Browse by Field',
      fields: [
        { path: 'browse.heading', label: 'Heading' },
        { path: 'browse.subtitle', label: 'Subtitle' },
      ],
    },
    {
      id: 'mission',
      title: 'Mission',
      fields: [
        { path: 'mission.eyebrow', label: 'Eyebrow' },
        { path: 'mission.heading', label: 'Heading' },
        { path: 'mission.body', label: 'Body', textarea: true },
      ],
    },
    {
      id: 'vision',
      title: 'Vision',
      fields: [
        { path: 'vision.eyebrow', label: 'Eyebrow' },
        { path: 'vision.heading', label: 'Heading' },
        { path: 'vision.body', label: 'Body', textarea: true },
      ],
    },
  ],

  about: [
    {
      id: 'header',
      title: 'Header',
      fields: [
        { path: 'header.eyebrow', label: 'Eyebrow' },
        { path: 'header.heading', label: 'Heading' },
        { path: 'header.intro', label: 'Intro', textarea: true, rows: 4 },
      ],
    },
    {
      id: 'mission',
      title: 'Mission',
      fields: [
        { path: 'mission.title', label: 'Title' },
        { path: 'mission.body', label: 'Body', textarea: true },
      ],
    },
    {
      id: 'vision',
      title: 'Vision',
      fields: [
        { path: 'vision.title', label: 'Title' },
        { path: 'vision.body', label: 'Body', textarea: true },
      ],
    },
    {
      id: 'pipelines',
      title: 'The three pipelines',
      fields: [{ path: 'pipelines.heading', label: 'Section heading' }],
      list: {
        path: 'pipelines.items',
        label: 'Pipelines',
        itemFields: [
          { key: 'title', label: 'Title' },
          { key: 'body', label: 'Body', textarea: true },
        ],
        blank: { title: 'New pipeline', body: '' },
      },
    },
    {
      id: 'roadmap',
      title: 'Roadmap',
      fields: [
        { path: 'roadmap.heading', label: 'Heading' },
        { path: 'roadmap.subtitle', label: 'Subtitle' },
      ],
      list: {
        path: 'roadmap.items',
        label: 'Roadmap steps',
        itemFields: [
          { key: 'phase', label: 'Phase' },
          { key: 'title', label: 'Title' },
          { key: 'body', label: 'Body', textarea: true },
        ],
        blank: { phase: 'Later', title: 'New step', body: '', state: 'next' },
      },
    },
    {
      id: 'teamCta',
      title: 'Team call-to-action',
      fields: [
        { path: 'teamCta.heading', label: 'Heading' },
        { path: 'teamCta.body', label: 'Body' },
        { path: 'teamCta.label', label: 'Button label' },
      ],
    },
    {
      id: 'footer',
      title: 'Footer note',
      fields: [{ path: 'footer.note', label: 'Note', textarea: true, rows: 3 }],
    },
  ],

  opportunities: [
    {
      id: 'header',
      title: 'Header',
      fields: [
        { path: 'header.eyebrow', label: 'Eyebrow' },
        { path: 'header.heading', label: 'Heading' },
        { path: 'header.intro', label: 'Intro', textarea: true, rows: 3 },
      ],
    },
  ],

  rankings: [
    {
      id: 'header',
      title: 'Header',
      fields: [
        { path: 'header.eyebrow', label: 'Eyebrow' },
        { path: 'header.heading', label: 'Heading' },
      ],
    },
  ],

  universities: [
    {
      id: 'header',
      title: 'Header',
      fields: [
        { path: 'header.eyebrow', label: 'Eyebrow' },
        { path: 'header.heading', label: 'Heading' },
        { path: 'header.subtitle', label: 'Subtitle', textarea: true },
      ],
    },
  ],

  fields: [
    {
      id: 'header',
      title: 'Header',
      fields: [{ path: 'header.heading', label: 'Heading' }],
    },
  ],

  team: [
    {
      id: 'header',
      title: 'Header',
      fields: [
        { path: 'header.eyebrow', label: 'Eyebrow' },
        { path: 'header.heading', label: 'Heading' },
        { path: 'header.subtitle', label: 'Subtitle', textarea: true },
        { path: 'header.emptyNote', label: 'Empty-state note' },
      ],
    },
  ],

  contact: [
    {
      id: 'header',
      title: 'Header',
      fields: [
        { path: 'header.eyebrow', label: 'Eyebrow' },
        { path: 'header.heading', label: 'Heading' },
        { path: 'header.intro', label: 'Intro', textarea: true, rows: 3 },
      ],
    },
    {
      id: 'details',
      title: 'Contact details',
      fields: [
        { path: 'email', label: 'Email' },
        { path: 'basedIn', label: 'Based in' },
      ],
    },
    {
      id: 'socials',
      title: 'Social links',
      fields: [
        { path: 'followHeading', label: 'Follow heading' },
        { path: 'socials.instagram', label: 'Instagram URL' },
        { path: 'socials.linkedin', label: 'LinkedIn URL' },
        { path: 'socials.x', label: 'X (Twitter) URL' },
        { path: 'footer', label: 'Footer note' },
      ],
    },
  ],
};

// Small helpers for reading/writing dot-paths inside a content object.
export function getPath(obj, path) {
  return path.split('.').reduce((o, k) => (o == null ? undefined : o[k]), obj);
}

export function setPath(obj, path, value) {
  const clone = JSON.parse(JSON.stringify(obj ?? {}));
  const keys = path.split('.');
  let node = clone;
  for (let i = 0; i < keys.length - 1; i++) {
    if (node[keys[i]] == null || typeof node[keys[i]] !== 'object') node[keys[i]] = {};
    node = node[keys[i]];
  }
  node[keys[keys.length - 1]] = value;
  return clone;
}
