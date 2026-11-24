import { Routes, Route, Navigate } from 'react-router-dom';
import { PlatformLayout } from '@/layouts/PlatformLayout';
import { AdminLayout } from '@/layouts/AdminLayout';
import { ProtectedRoute, RequirePermission } from '@/components/ProtectedRoute';

import Platform from '@/pages/Platform';
import Login from '@/pages/Login';
import StudentCleanup from '@/pages/admin/StudentCleanup';
import StudentStudy from '@/pages/student/Study';
import StudyQuestionnaire from '@/pages/student/StudyQuestionnaire';
import Classroom from '@/pages/admin/Classroom';
import Privacy from '@/pages/student/Privacy';
import Applications from '@/pages/Applications';
import School from '@/pages/School';
import RecruiterRegister from '@/pages/RecruiterRegister';
import StudentRegister from '@/pages/StudentRegister';
import NotFound from '@/pages/NotFound';

// Public data surfaces (PRS v2.0 — un-gated for launch).
import Rankings from '@/pages/Rankings';
import Fields from '@/pages/Fields';
import Universities from '@/pages/Universities';
import UniversityProfile from '@/pages/UniversityProfile';
import StudentProfile from '@/pages/StudentProfile';
import About from '@/pages/About';
import Team from '@/pages/Team';
import Contact from '@/pages/Contact';
import OpportunityPortal from '@/pages/Opportunities';

// Student self-service.
import StudentLayout from '@/layouts/StudentLayout';
import StudentDashboard from '@/pages/student/Dashboard';
import StudentProfileBuilder from '@/pages/student/ProfileBuilder';

// Employer.
import EmployerLayout from '@/layouts/EmployerLayout';
import EmployerDashboard from '@/pages/employer/Dashboard';
import EmployerSearch from '@/pages/employer/Search';
import EmployerSaved from '@/pages/employer/Saved';
import EmployerOpportunities from '@/pages/employer/Opportunities';
import EmployerProfile from '@/pages/employer/Profile';

import AdminDashboard from '@/pages/admin/Dashboard';
import EvaluatedScores from '@/pages/admin/EvaluatedScores';
import AdminAnalytics from '@/pages/admin/Analytics';
import DepartmentRankings from '@/pages/admin/DepartmentRankings';
import Settings from '@/pages/admin/Settings';
import Cycles from '@/pages/admin/Cycles';
import Approvals from '@/pages/admin/Approvals';
import Profile from '@/pages/admin/Profile';
import ChangePassword from '@/pages/admin/ChangePassword';
import Team_Admin from '@/pages/admin/Team';
import Recruiters from '@/pages/admin/Recruiters';
import SiteEditor from '@/pages/admin/SiteEditor';
import TestAccounts from '@/pages/admin/TestAccounts';
// Admin v2.0 surfaces.
import AdminFlags from '@/pages/admin/Flags';
import AdminVerification from '@/pages/admin/Verification';
import AdminScoringWeights from '@/pages/admin/ScoringWeights';
import AdminReports from '@/pages/admin/Reports';
import AdminOpportunities from '@/pages/admin/Opportunities';
import AdminModeration from '@/pages/admin/Moderation';

// Helper: wrap an element in a permission gate.
const gated = (permission, element) => <RequirePermission permission={permission}>{element}</RequirePermission>;

export function AppRoutes() {
  return (
    <Routes>
      {/* Retired at launch: the "launching soon" page at /welcome and the
          duplicate hub at /platform. There is ONE landing page now, at "/".
          Both old paths redirect so existing links, bookmarks and any shared
          posts still land somewhere sensible instead of on the 404. */}
      <Route path="/welcome" element={<Navigate to="/" replace />} />
      <Route path="/platform" element={<Navigate to="/" replace />} />

      {/* Public surfaces — the landing page plus every browsable page. */}
      <Route element={<PlatformLayout />}>
        <Route index element={<Platform />} />
        <Route path="rankings" element={<Rankings />} />
        <Route path="fields" element={<Fields />} />
        <Route path="fields/:slug" element={<Fields />} />
        <Route path="universities" element={<Universities />} />
        <Route path="universities/:slug" element={<UniversityProfile />} />
        <Route path="students/:id" element={<StudentProfile />} />
        <Route path="opportunities" element={<OpportunityPortal />} />
        <Route path="about" element={<About />} />
        <Route path="team" element={<Team />} />
        <Route path="contact" element={<Contact />} />
      </Route>

      {/* Auth + registration. */}
      <Route path="/school" element={<School />} />
      <Route path="/login" element={<Login />} />
      <Route path="/signup" element={<Login />} />
      <Route path="/recruiter-register" element={<RecruiterRegister />} />
      <Route path="/student-register" element={<StudentRegister />} />

      {/* Student self-service (StudentLayout self-guards on role). */}
      <Route path="/student" element={<StudentLayout />}>
        <Route index element={<StudentDashboard />} />
        <Route path="profile" element={<StudentProfileBuilder />} />
        <Route path="privacy" element={<Privacy />} />
        <Route path="study" element={<StudentStudy />} />
        <Route path="questionnaire" element={<StudyQuestionnaire />} />
        <Route path="applications" element={<Applications />} />
      </Route>

      {/* Employer (EmployerLayout self-guards on role). */}
      <Route path="/employer" element={<EmployerLayout />}>
        <Route index element={<EmployerDashboard />} />
        <Route path="search" element={<EmployerSearch />} />
        <Route path="saved" element={<EmployerSaved />} />
        <Route path="opportunities" element={<EmployerOpportunities />} />
        <Route path="profile" element={<EmployerProfile />} />
        <Route path="applications" element={<Applications />} />
      </Route>

      {/* Admin dashboard. */}
      <Route
        path="/admin"
        element={
          <ProtectedRoute>
            <AdminLayout />
          </ProtectedRoute>
        }
      >
        <Route index element={<AdminDashboard />} />
        <Route path="student-cleanup" element={<StudentCleanup />} />
        <Route path="classroom" element={<Classroom />} />
        <Route path="profile" element={<Profile />} />
        <Route path="change-password" element={<ChangePassword />} />
        <Route path="cycles" element={gated('manage_cycles', <Cycles />)} />
        <Route path="approvals" element={gated('approve_students', <Approvals />)} />
        <Route path="recruiters" element={gated('approve_recruiters', <Recruiters />)} />
        <Route path="scores" element={gated('view_analytics', <EvaluatedScores />)} />
        <Route path="analytics" element={gated('view_analytics', <AdminAnalytics />)} />
        <Route path="departments" element={gated('view_analytics', <DepartmentRankings />)} />
        <Route path="team" element={gated('manage_team', <Team_Admin />)} />
        <Route path="test-accounts" element={gated('manage_team', <TestAccounts />)} />
        <Route path="site" element={gated('manage_site', <SiteEditor />)} />
        {/* Ungated: this is the signed-in user's own account page. It was gated
            on view_analytics, which locked a manage_site-only admin out of the
            rankings-visibility control living on it. The control self-gates. */}
        <Route path="settings" element={<Settings />} />
        {/* PRS v2.0 admin surfaces. */}
        <Route path="flags" element={gated('approve_students', <AdminFlags />)} />
        <Route path="verification" element={gated('approve_students', <AdminVerification />)} />
        <Route path="scoring" element={gated('view_analytics', <AdminScoringWeights />)} />
        <Route path="reports" element={gated('view_analytics', <AdminReports />)} />
        <Route path="opportunities" element={gated('view_analytics', <AdminOpportunities />)} />
        <Route path="moderation" element={gated('view_analytics', <AdminModeration />)} />
      </Route>

      <Route path="/404" element={<NotFound />} />
      <Route path="*" element={<Navigate to="/404" replace />} />
    </Routes>
  );
}
