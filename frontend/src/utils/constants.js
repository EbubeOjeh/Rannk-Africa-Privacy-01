export const ROLES = {
  SUPER_ADMIN: 'super_admin',
  SCHOOL_ADMIN: 'school_admin',
  UNIVERSITY_ADMIN: 'university_admin', // legacy alias of school_admin
  STUDENT: 'student',
  EMPLOYER: 'employer',
  EVALUATOR: 'evaluator',
};

export const SCHOOL_ADMIN_ROLES = [ROLES.SCHOOL_ADMIN, ROLES.UNIVERSITY_ADMIN];

export const isSchoolAdmin = (role) =>
  role === ROLES.SUPER_ADMIN || SCHOOL_ADMIN_ROLES.includes(role);

export const isSuperAdmin = (role) => role === ROLES.SUPER_ADMIN;

// Final / pipeline maxima — spec: Academic /40 + Project /40 + Achievements /20 = /100.
export const SCORE_MAX = {
  ACADEMIC: 40,
  PROJECT: 40,
  ACHIEVEMENT: 20,
  FINAL: 100,
};

export const ACHIEVEMENT_TYPES = [
  { type: 'internship', label: 'Internship', points: 3 },
  { type: 'hackathon_participation', label: 'Hackathon Participation', points: 2 },
  { type: 'hackathon_win', label: 'Hackathon Win', points: 5 },
  { type: 'leadership_role', label: 'Leadership Role', points: 5 },
  { type: 'publication', label: 'Publication', points: 6 },
  { type: 'startup_built', label: 'Startup Built', points: 8 },
];

export const ACHIEVEMENT_CAP = 20;

// Nigerian states — used for state filtering on the leaderboard.
export const NIGERIAN_STATES = [
  'Abia', 'Adamawa', 'Akwa Ibom', 'Anambra', 'Bauchi', 'Bayelsa', 'Benue',
  'Borno', 'Cross River', 'Delta', 'Ebonyi', 'Edo', 'Ekiti', 'Enugu',
  'FCT', 'Gombe', 'Imo', 'Jigawa', 'Kaduna', 'Kano', 'Katsina', 'Kebbi',
  'Kogi', 'Kwara', 'Lagos', 'Nasarawa', 'Niger', 'Ogun', 'Ondo', 'Osun',
  'Oyo', 'Plateau', 'Rivers', 'Sokoto', 'Taraba', 'Yobe', 'Zamfara',
];

export const FIELD_COLORS = {
  tech: { bg: 'bg-emerald-500/15', text: 'text-emerald-300', dot: 'bg-emerald-400' },
  'computer-science': { bg: 'bg-amber-500/15', text: 'text-amber-200', dot: 'bg-amber-400' },
  engineering: { bg: 'bg-orange-500/15', text: 'text-orange-300', dot: 'bg-orange-400' },
  'data-science': { bg: 'bg-cyan-500/15', text: 'text-cyan-300', dot: 'bg-cyan-400' },
  'information-technology': { bg: 'bg-teal-500/15', text: 'text-teal-300', dot: 'bg-teal-400' },
};

export const fieldStyle = (slug) =>
  FIELD_COLORS[slug?.toLowerCase()] || {
    bg: 'bg-cream/5',
    text: 'text-cream/80',
    dot: 'bg-cream/40',
  };
