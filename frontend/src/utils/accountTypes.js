import { ShieldCheck, Briefcase, GraduationCap } from 'lucide-react';

/**
 * The audiences that can sign in to RankAfrica. The backend has a single
 * /auth/login endpoint (role comes back on the user), so these entries only
 * tailor the *presentation* — heading, copy, icon and the matching register
 * link — so each kind of user feels addressed directly.
 */
export const ACCOUNT_TYPES = {
  employee: {
    key: 'employee',
    label: 'Staff Sign In',
    short: 'Staff',
    icon: ShieldCheck,
    title: 'Staff Sign In',
    blurb: 'Staff access to the RankAfrica admin dashboard.',
    register: null,
  },
  recruiter: {
    key: 'recruiter',
    label: 'Recruiter / Organization',
    short: 'Recruiter',
    icon: Briefcase,
    title: 'Recruiter Sign In',
    blurb: 'Discover and connect with top-ranked students.',
    register: { to: '/recruiter-register', label: 'Request recruiter access' },
  },
  student: {
    key: 'student',
    label: 'Student',
    short: 'Student',
    icon: GraduationCap,
    title: 'Student Sign In',
    blurb: 'Access your RankAfrica student profile.',
    register: { to: '/student-register', label: 'Create your student profile' },
  },
};

// Public audiences first; internal staff sign-in is kept last (and visually
// separated in the menu) so the entry point most users need is up top.
// RankAfrica is fully student-driven — students self-register and manage their
// own profiles; there is no school/university sign-in.
export const ACCOUNT_TYPE_LIST = [
  ACCOUNT_TYPES.recruiter,
  ACCOUNT_TYPES.student,
  ACCOUNT_TYPES.employee,
];
