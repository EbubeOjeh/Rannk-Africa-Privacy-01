import AuthorizedImage from '@/components/AuthorizedImage';
import { useEffect, useMemo, useState } from 'react';
import Privacy from './Privacy';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  User,
  Link2,
  Lightbulb,
  FlaskConical,
  Briefcase,
  Trophy,
  Users,
  Award,
  Upload,
  Trash2,
  Plus,
  ArrowRight,
  CheckCircle2,
  Clock,
  XCircle,
  Sparkles,
  Loader2,
  FileText,
  Music,
} from 'lucide-react';
import toast from 'react-hot-toast';
import { studentService } from '@/services/student.service';
import { Loader } from '@/components/Loader';
import { SuccessModal } from '@/components/SuccessModal';
import { PageGuide } from '@/components/PageGuide';

/* ──────────────────────────────────────────────────────────────────────────
 *  Enum option sets (mirrors the API contract). Each is [value, friendlyLabel].
 * ──────────────────────────────────────────────────────────────────────── */
const RESEARCH_TYPES = [
  ['journal_publication', 'Journal Publication'],
  ['conference_paper', 'Conference Paper'],
  ['undergraduate_research', 'Undergraduate Research'],
  ['research_assistantship', 'Research Assistantship'],
  ['book_chapter', 'Book Chapter'],
];
const EXPERIENCE_TYPES = [
  ['internship', 'Internship'],
  ['volunteer', 'Volunteer'],
  ['startup', 'Startup'],
  ['business', 'Business'],
  ['employment', 'Employment'],
];
const COMPETITION_TYPES = [
  ['hackathon', 'Hackathon'],
  ['moot_court', 'Moot Court'],
  ['business_competition', 'Business Competition'],
  ['debate', 'Debate'],
  ['music_award', 'Music Award'],
  ['innovation_challenge', 'Innovation Challenge'],
];
const COMPETITION_RESULTS = [
  ['winner', 'Winner'],
  ['runner_up', 'Runner-up'],
  ['finalist', 'Finalist'],
  ['participant', 'Participant'],
];
const LEADERSHIP_TYPES = [
  ['student_leadership', 'Student Leadership'],
  ['volunteer_work', 'Volunteer Work'],
  ['community_impact', 'Community Impact'],
  ['professional_org', 'Professional Organisation'],
];
// Contract lists 9 achievement types; we surface the first six friendly ones.
const ACHIEVEMENT_TYPES = [
  ['award', 'Award'],
  ['certification', 'Certification'],
  ['scholarship', 'Scholarship'],
  ['grant', 'Grant'],
  ['fellowship', 'Fellowship'],
  ['national_recognition', 'National Recognition'],
];

const GPA_SCALES = [
  ['4.0', '4.0'],
  ['5.0', '5.0'],
  ['7.0', '7.0'],
];
// RankAfrica currently ranks final-year undergraduates only, so academic level
// and year of study are fixed rather than user-selectable (mirrors the read-only
// labels on the registration form).
const ACADEMIC_LEVEL_LABEL = 'Synthetic study profile';
const YEAR_OF_STUDY_LABEL = 'Not collected for this study';
const GENDERS = [
  ['male', 'Male'],
  ['female', 'Female'],
  ['other', 'Other'],
  ['prefer_not_to_say', 'Prefer not to say'],
];

// Sections depend on the student's field. Technology & Music use the PROJECT
// model (Projects + the structured achievement sections); every other field
// uses the PROFILE model (a single free-text "Profile Assessment" scored /60).
// An unknown/missing field falls back to the project model, matching the
// backend default (DEFAULT_FIELD = technology).
const PROJECT_MODEL_FIELDS = ['technology', 'music'];

/**
 * The ordered section list for a given field slug. Kept as a pure function of
 * the slug (rather than closing over `profile`) because saving the Details
 * section can re-map the student's field — and therefore change this very list
 * — in the same request that triggers the advance. See `goNext`.
 */
function buildTabs(fieldSlug) {
  const isProjectModel = !fieldSlug || PROJECT_MODEL_FIELDS.includes(fieldSlug);
  const isMusic = fieldSlug === 'music';
  const base = [
    { key: 'details', label: 'Details', icon: User },
    { key: 'links', label: 'Links & CV', icon: Link2 },
    { key: 'privacy', label: 'Privacy', icon: User },
  ];
  if (isProjectModel) {
    return [
      ...base,
      { key: 'projects', label: isMusic ? 'Portfolio' : 'Projects', icon: isMusic ? Music : Lightbulb },
      { key: 'research', label: 'Research', icon: FlaskConical },
      { key: 'experience', label: 'Experience', icon: Briefcase },
      { key: 'competitions', label: 'Competitions', icon: Trophy },
      { key: 'leadership', label: 'Leadership', icon: Users },
      { key: 'achievements', label: 'Achievements', icon: Award },
    ];
  }
  return [...base, { key: 'assessment', label: 'Profile Assessment', icon: Sparkles }];
}

const toList = (csv) =>
  String(csv || '')
    .split(',')
    .map((s) => s.trim())
    .filter(Boolean);

export default function StudentProfileBuilder() {
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [tab, setTab] = useState('details');
  const [complete, setComplete] = useState(false);
  const navigate = useNavigate();

  const reload = () =>
    studentService
      .me()
      .then(setProfile)
      .catch((err) =>
        toast.error(err?.response?.data?.error?.message || 'Could not load your profile.')
      );

  useEffect(() => {
    reload().finally(() => setLoading(false));
  }, []);

  const tabs = useMemo(() => buildTabs(profile?.field_slug), [profile?.field_slug]);
  const activeTab = tabs.some((t) => t.key === tab) ? tab : 'details';
  const stepNumber = Math.max(0, tabs.findIndex((t) => t.key === activeTab)) + 1;

  /**
   * Advance to the next section, or finish. Sections call this after they save.
   *
   * `fieldSlug` is the slug from the SAVE RESPONSE, not from state: saving the
   * Details section re-maps the student's field from their course, which can
   * swap them between the 3-section and 8-section flow. Recomputing the list
   * from the response keeps the advance correct on that turn — using the
   * memoized `tabs` would index into a list that is about to be replaced.
   */
  const goNext = (fieldSlug) => {
    const list = buildTabs(fieldSlug === undefined ? profile?.field_slug : fieldSlug);
    const next = list[list.findIndex((t) => t.key === activeTab) + 1];
    if (next) {
      setTab(next.key);
      window.scrollTo({ top: 0, behavior: 'smooth' });
    } else {
      setComplete(true);
    }
  };

  if (loading) return <Loader label="Loading your profile…" />;
  if (!profile) return <p className="text-cream/60">Could not load your profile.</p>;

  return (
    <div className="space-y-6">
      <PageGuide
        id="student-profile-builder"
        title="Building your profile"
        steps={[
          'Work through the sections in order — each one ends in “Save & continue”, which takes you to the next.',
          'Sections other than Details can be skipped and filled in later; nothing is lost if you come back.',
          'When you finish the last section you will see a confirmation that your registration is complete.',
        ]}
      />
      <div>
        <h1 className="font-display text-2xl font-bold">Profile builder</h1>
        <p className="text-sm text-cream/60 mt-1">
          Step {stepNumber} of {tabs.length} — the more complete and verified your profile, the
          higher you rank.
        </p>
      </div>

      {/* Tabs */}
      <div className="flex flex-wrap gap-1.5 border-b border-cream/10 pb-3">
        {tabs.map((t) => (
          <button
            key={t.key}
            onClick={() => setTab(t.key)}
            className={`inline-flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
              activeTab === t.key
                ? 'bg-gold-400/15 text-gold-300'
                : 'text-white/70 hover:text-white hover:bg-white/5'
            }`}
          >
            <t.icon className="w-4 h-4" />
            {t.label}
          </button>
        ))}
      </div>

      <motion.div
        key={activeTab}
        initial={{ opacity: 0, y: 6 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.2 }}
      >
        {activeTab === 'privacy' && <Privacy />}
        {activeTab === 'details' && (
          <DetailsTab profile={profile} onSaved={setProfile} onDone={goNext} />
        )}
        {activeTab === 'links' && (
          <LinksTab profile={profile} onSaved={setProfile} onDone={goNext} />
        )}
        {activeTab === 'assessment' && (
          <AssessmentTab profile={profile} onSaved={setProfile} onDone={goNext} />
        )}
        {activeTab === 'projects' && (
          <ProjectsTab
            onChange={reload}
            onDone={goNext}
            isMusic={profile?.field_slug === 'music'}
          />
        )}
        {activeTab === 'research' && <ResearchTab onChange={reload} onDone={goNext} />}
        {activeTab === 'experience' && <ExperienceTab onChange={reload} onDone={goNext} />}
        {activeTab === 'competitions' && <CompetitionsTab onChange={reload} onDone={goNext} />}
        {activeTab === 'leadership' && <LeadershipTab onChange={reload} onDone={goNext} />}
        {activeTab === 'achievements' && <AchievementsTab onChange={reload} onDone={goNext} />}
      </motion.div>

      {/* Fires once the student advances past the final section. */}
      <SuccessModal
        open={complete}
        title="Registration Complete!"
        cta="Go to my dashboard"
        onClose={() => {
          setComplete(false);
          navigate('/student', { replace: true });
        }}
      >
        Thank you for registering with Rank Africa. Follow our social media pages for updates.
        Discovery remains private until you enable an audience and save. Scores are illustrative classroom data.
      </SuccessModal>
    </div>
  );
}

/* ────────────────────────────── shared bits ─────────────────────────────── */

function Field({ label, children, full }) {
  return (
    <div className={full ? 'sm:col-span-2' : ''}>
      <label className="field-label">{label}</label>
      {children}
    </div>
  );
}

function Text({ value, onChange, ...rest }) {
  return <input className="input" value={value ?? ''} onChange={(e) => onChange(e.target.value)} {...rest} />;
}

function Area({ value, onChange, rows = 3, ...rest }) {
  return (
    <textarea
      className="input"
      rows={rows}
      value={value ?? ''}
      onChange={(e) => onChange(e.target.value)}
      {...rest}
    />
  );
}

function Select({ value, onChange, options, placeholder, ...rest }) {
  return (
    <select className="input" value={value ?? ''} onChange={(e) => onChange(e.target.value)} {...rest}>
      {placeholder && <option value="">{placeholder}</option>}
      {options.map(([v, label]) => (
        <option key={v} value={v}>
          {label}
        </option>
      ))}
    </select>
  );
}

function SectionCard({ title, description, icon: Icon, children }) {
  return (
    <div className="card p-6">
      <div className="flex items-start gap-3">
        {Icon && (
          <span className="w-9 h-9 shrink-0 rounded-lg bg-gold-400/15 grid place-content-center text-gold-400">
            <Icon className="w-4 h-4" />
          </span>
        )}
        <div>
          <h2 className="font-display text-lg font-bold">{title}</h2>
          {description && <p className="text-sm text-cream/55 mt-0.5">{description}</p>}
        </div>
      </div>
      <div className="mt-5">{children}</div>
    </div>
  );
}

function VerifyBadge({ status }) {
  const s = status || 'pending';
  if (s === 'verified')
    return (
      <span className="pill-success">
        <CheckCircle2 className="w-3 h-3" /> Verified
      </span>
    );
  if (s === 'rejected')
    return (
      <span className="pill-danger">
        <XCircle className="w-3 h-3" /> Rejected
      </span>
    );
  return (
    <span className="pill-pending">
      <Clock className="w-3 h-3" /> Pending
    </span>
  );
}

/* ────────────────────────────── Details tab ─────────────────────────────── */

function DetailsTab({ profile, onSaved, onDone }) {
  const classroom = (profile.email || "").endsWith("@study.rankafrica.example");
  const [form, setForm] = useState({
    full_name: profile.full_name || '',
    bio: profile.bio || '',
    gender: profile.gender || '',
    course: profile.course || '',
    faculty: profile.faculty || '',
    raw_cgpa: profile.raw_cgpa ?? '',
    gpa_scale: profile.gpa_scale ? String(profile.gpa_scale) : '',
    skills: (profile.skills || []).join(', '),
    languages: (profile.languages || []).join(', '),
  });
  const [saving, setSaving] = useState(false);
  const [avatarBusy, setAvatarBusy] = useState(false);
  const [transcriptBusy, setTranscriptBusy] = useState(false);
  const set = (k) => (v) => setForm((f) => ({ ...f, [k]: v }));

  const save = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      const payload = {
        full_name: form.full_name,
        bio: form.bio,
        gender: form.gender || null,
        course: form.course,
        faculty: form.faculty,
        skills: toList(form.skills),
        languages: toList(form.languages),
      };
      if (form.raw_cgpa !== '') payload.raw_cgpa = Number(form.raw_cgpa);
      if (form.gpa_scale !== '') payload.gpa_scale = Number(form.gpa_scale);
      const updated = await studentService.updateMe(payload);
      onSaved(updated);
      toast.success('Profile updated.');
      // Saving the course can re-map the field (and therefore the section
      // list), so hand the fresh slug to the parent rather than letting it
      // read stale state.
      onDone?.(updated?.field_slug);
    } catch (err) {
      toast.error(err?.response?.data?.error?.message || 'Could not save.');
    } finally {
      setSaving(false);
    }
  };

  const onTranscript = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setTranscriptBusy(true);
    try {
      const updated = await studentService.uploadTranscript(file);
      onSaved(updated);
      toast.success('Transcript uploaded.');
    } catch (err) {
      toast.error(err?.response?.data?.error?.message || 'Upload failed.');
    } finally {
      setTranscriptBusy(false);
      e.target.value = '';
    }
  };

  const onAvatar = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setAvatarBusy(true);
    try {
      const updated = await studentService.uploadAvatar(file);
      onSaved(updated);
      toast.success('Photo updated.');
    } catch (err) {
      toast.error(err?.response?.data?.error?.message || 'Upload failed.');
    } finally {
      setAvatarBusy(false);
      e.target.value = '';
    }
  };

  return (
    <form onSubmit={save}>
      <SectionCard
        title="Your details"
        description={classroom ? "Assigned school and academic record are fixed. Your chosen photo stays out of discovery until you save photo sharing for an enabled audience." : "Your name, academic standing and skills."}
        icon={User}
      >
        {/* Avatar */}
        <div className="flex items-center gap-4 mb-6">
          <div className="w-16 h-16 rounded-full bg-cream/5 border border-cream/10 overflow-hidden grid place-content-center">
            {profile.avatar_url ? (
              <AuthorizedImage src={profile.avatar_url} alt="" className="w-full h-full object-cover" />
            ) : (
              <User className="w-6 h-6 text-cream/40" />
            )}
          </div>
          <label className="btn-ghost text-xs cursor-pointer">
            {avatarBusy ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <Upload className="w-4 h-4" />
            )}
            {avatarBusy ? 'Uploading…' : 'Change photo'}
            <input type="file" accept="image/*" className="hidden" onChange={onAvatar} />
          </label>
        </div>

        <div className="grid sm:grid-cols-2 gap-4">
          <Field label="Full name">
            <Text value={form.full_name} onChange={set('full_name')} placeholder="Full name" />
          </Field>
          <Field label="Gender">
            <Select value={form.gender} onChange={set('gender')} options={GENDERS} placeholder="Prefer not to say" />
          </Field>
          <Field label="Bio" full>
            <Area value={form.bio} onChange={set('bio')} placeholder="A short summary about you" />
          </Field>
          <Field label="Course / Programme">
            <Text disabled={classroom} value={form.course} onChange={set('course')} placeholder="e.g. Computer Science" />
          </Field>
          <Field label="Faculty">
            <Text disabled={classroom} value={form.faculty} onChange={set('faculty')} placeholder="e.g. Engineering" />
          </Field>
          <Field label="Academic level">
            <div className="input flex items-center text-cream/80 cursor-default select-none">
              {ACADEMIC_LEVEL_LABEL}
            </div>
          </Field>
          <Field label="Year of study">
            <div className="input flex items-center text-cream/80 cursor-default select-none">
              {YEAR_OF_STUDY_LABEL}
            </div>
          </Field>
          <Field label="CGPA">
            <Text
              type="number"
              step="0.01"
              min="0"
              disabled={classroom}
              value={form.raw_cgpa}
              onChange={set('raw_cgpa')}
              placeholder="e.g. 4.52"
            />
          </Field>
          <Field label="GPA scale">
            <Select disabled={classroom} value={form.gpa_scale} onChange={set('gpa_scale')} options={GPA_SCALES} placeholder="Select scale" />
          </Field>
          <Field label="Skills (comma separated)" full>
            <Text value={form.skills} onChange={set('skills')} placeholder="Python, Data Analysis, UI Design" />
          </Field>
          <Field label="Languages (comma separated)" full>
            <Text value={form.languages} onChange={set('languages')} placeholder="English, French, Yoruba" />
          </Field>
        </div>

        {/* Unofficial transcript upload — backs the CGPA above. */}
        <div className="mt-6 rounded-xl border border-cream/10 bg-ink-900/40 px-4 py-4">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div className="flex items-center gap-3 min-w-0">
              <span className="w-9 h-9 shrink-0 rounded-lg bg-cream/5 grid place-content-center text-gold-400">
                <FileText className="w-4 h-4" />
              </span>
              <div className="min-w-0">
                <p className="text-sm font-medium text-white">Unofficial transcript / semester results</p>
                {profile.transcript_url ? (
                  <a
                    href={profile.transcript_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-xs text-gold-300 hover:underline"
                  >
                    View current transcript
                  </a>
                ) : (
                  <p className="text-xs text-cream/50">PDF, image or document.</p>
                )}
              </div>
            </div>
            <label className="btn-ghost text-xs cursor-pointer">
              {transcriptBusy ? <Loader2 className="w-4 h-4 animate-spin" /> : <Upload className="w-4 h-4" />}
              {transcriptBusy
                ? 'Uploading…'
                : profile.transcript_url
                ? 'Replace transcript'
                : 'Upload transcript'}
              <input
                type="file"
                accept=".pdf,.doc,.docx,image/*"
                className="hidden"
                onChange={onTranscript}
              />
            </label>
          </div>
          <p className="mt-3 text-xs text-cream/60 leading-relaxed">
            Official transcripts may not yet be available for final-year students. Please upload your
            latest unofficial transcript or semester results covering all completed semesters:
          </p>
          <ul className="mt-1.5 text-xs text-cream/55 list-disc pl-5 space-y-0.5">
            <li>
              <span className="text-cream/80">4-year programmes:</span> results covering 100 Level to
              300 Level.
            </li>
            <li>
              <span className="text-cream/80">5-year programmes:</span> results covering 100 Level to
              400 Level.
            </li>
          </ul>
        </div>

        {/* Uploads are separate in-flight requests; advancing while one is
            running would unmount this tab and drop the result. */}
        <button
          type="submit"
          disabled={saving || avatarBusy || transcriptBusy}
          className="btn-primary mt-6"
        >
          {saving ? 'Saving…' : 'Save & continue'}
          {!saving && <ArrowRight className="w-4 h-4" />}
        </button>
      </SectionCard>
    </form>
  );
}

/* ─────────────────────────────── Links tab ──────────────────────────────── */

function LinksTab({ profile, onSaved, onDone }) {
  const [form, setForm] = useState({
    whatsapp_number: profile.whatsapp_number || '',
    phone_number: profile.phone_number || '',
    linkedin_url: profile.linkedin_url || '',
    github_url: profile.github_url || '',
    behance_url: profile.behance_url || '',
    portfolio_url: profile.portfolio_url || '',
    google_scholar_url: profile.google_scholar_url || '',
    music_url: profile.music_url || '',
  });
  const [saving, setSaving] = useState(false);
  const [cvBusy, setCvBusy] = useState(false);
  const set = (k) => (v) => setForm((f) => ({ ...f, [k]: v }));

  const save = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      const updated = await studentService.updateMe(form);
      onSaved(updated);
      toast.success('Links updated.');
      onDone?.(updated?.field_slug);
    } catch (err) {
      toast.error(err?.response?.data?.error?.message || 'Could not save.');
    } finally {
      setSaving(false);
    }
  };

  const onResume = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setCvBusy(true);
    try {
      const updated = await studentService.uploadResume(file);
      onSaved(updated);
      toast.success('CV uploaded.');
    } catch (err) {
      toast.error(err?.response?.data?.error?.message || 'Upload failed.');
    } finally {
      setCvBusy(false);
      e.target.value = '';
    }
  };

  return (
    <form onSubmit={save}>
      <SectionCard title="Links & CV" description="Where recruiters can learn more about you." icon={Link2}>
        <div className="grid sm:grid-cols-2 gap-4">
          <Field label="LinkedIn">
            <Text value={form.linkedin_url} onChange={set('linkedin_url')} placeholder="https://linkedin.com/in/…" />
          </Field>
          <Field label="GitHub">
            <Text value={form.github_url} onChange={set('github_url')} placeholder="https://github.com/…" />
          </Field>
          <Field label="Behance">
            <Text value={form.behance_url} onChange={set('behance_url')} placeholder="https://behance.net/…" />
          </Field>
          <Field label="Portfolio">
            <Text value={form.portfolio_url} onChange={set('portfolio_url')} placeholder="https://…" />
          </Field>
          <Field label="Google Scholar">
            <Text value={form.google_scholar_url} onChange={set('google_scholar_url')} placeholder="https://scholar.google.com/…" />
          </Field>
          <Field label="Music (Spotify / SoundCloud)">
            <Text value={form.music_url} onChange={set('music_url')} placeholder="https://…" />
          </Field>
          <Field label="WhatsApp number">
            <Text value={form.whatsapp_number} onChange={set('whatsapp_number')} placeholder="+234…" />
          </Field>
          <Field label="Phone number">
            <Text value={form.phone_number} onChange={set('phone_number')} placeholder="+234…" />
          </Field>
        </div>

        {/* CV / resume upload */}
        <div className="mt-6 rounded-xl border border-cream/10 bg-ink-900/40 px-4 py-4 flex flex-wrap items-center justify-between gap-3">
          <div className="flex items-center gap-3 min-w-0">
            <span className="w-9 h-9 shrink-0 rounded-lg bg-cream/5 grid place-content-center text-gold-400">
              <FileText className="w-4 h-4" />
            </span>
            <div className="min-w-0">
              <p className="text-sm font-medium text-white">CV / Résumé</p>
              {profile.resume_url ? (
                <a
                  href={profile.resume_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-xs text-gold-300 hover:underline"
                >
                  View current CV
                </a>
              ) : (
                <p className="text-xs text-cream/50">PDF or DOC, uploaded once.</p>
              )}
            </div>
          </div>
          <label className="btn-ghost text-xs cursor-pointer">
            {cvBusy ? <Loader2 className="w-4 h-4 animate-spin" /> : <Upload className="w-4 h-4" />}
            {cvBusy ? 'Uploading…' : profile.resume_url ? 'Replace CV' : 'Upload CV'}
            <input
              type="file"
              accept=".pdf,.doc,.docx"
              className="hidden"
              onChange={onResume}
            />
          </label>
        </div>

        <button type="submit" disabled={saving || cvBusy} className="btn-primary mt-6">
          {saving ? 'Saving…' : 'Save & continue'}
          {!saving && <ArrowRight className="w-4 h-4" />}
        </button>
      </SectionCard>
    </form>
  );
}

/* ──────────────────── generic list + add-form for sub-entities ───────────── */

/**
 * Renders an existing list of items plus an inline "add" form. The caller
 * supplies how to load/create/delete and how to render a row + the add form
 * fields, so every sub-entity tab reuses this shell.
 *
 * These sections have no natural completion event (a student may add one item,
 * ten, or none), so they get an explicit footer control that calls `onDone` to
 * move the registration flow forward. Advancing is deliberately NOT wired into
 * `add` — students add several items in a row, and unmounting on the first one
 * would hide the row they just created.
 */
function EntitySection({
  title,
  description,
  icon,
  load,
  create,
  remove,
  blankForm,
  renderRow,
  renderForm,
  onChange,
  onDone,
  extraRowAction,
  continueHint,
}) {
  const [items, setItems] = useState(null);
  const [form, setForm] = useState(blankForm);
  const [saving, setSaving] = useState(false);
  const [busyId, setBusyId] = useState(null);
  const set = (k) => (v) => setForm((f) => ({ ...f, [k]: v }));

  const refresh = () => load().then(setItems).catch(() => setItems([]));
  useEffect(() => {
    refresh();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const add = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      await create(form);
      setForm(blankForm);
      toast.success(`${title.replace(/s$/, '')} added.`);
      await refresh();
      onChange?.();
    } catch (err) {
      toast.error(err?.response?.data?.error?.message || 'Could not add.');
    } finally {
      setSaving(false);
    }
  };

  const del = async (id) => {
    setBusyId(id);
    try {
      await remove(id);
      setItems((list) => (list || []).filter((x) => x.id !== id));
      toast.success('Removed.');
      onChange?.();
    } catch (err) {
      toast.error(err?.response?.data?.error?.message || 'Could not remove.');
    } finally {
      setBusyId(null);
    }
  };

  return (
    <SectionCard title={title} description={description} icon={icon}>
      {/* Existing items */}
      {items === null ? (
        <p className="text-sm text-cream/50">Loading…</p>
      ) : items.length === 0 ? (
        <p className="text-sm text-cream/50">Nothing added yet — use the form below.</p>
      ) : (
        <ul className="space-y-2">
          {items.map((it) => (
            <li
              key={it.id}
              className="flex items-start justify-between gap-3 rounded-xl border border-cream/10 bg-ink-900/40 px-4 py-3"
            >
              <div className="min-w-0">{renderRow(it)}</div>
              <div className="flex items-center gap-1 shrink-0">
                {extraRowAction?.(it, refresh)}
                <button
                  onClick={() => del(it.id)}
                  disabled={busyId === it.id}
                  className="btn-ghost h-8 w-8 p-0 text-rose-300"
                  title="Remove"
                >
                  {busyId === it.id ? (
                    <Loader2 className="w-3.5 h-3.5 animate-spin" />
                  ) : (
                    <Trash2 className="w-3.5 h-3.5" />
                  )}
                </button>
              </div>
            </li>
          ))}
        </ul>
      )}

      {/* Add form */}
      <form onSubmit={add} className="mt-5 pt-5 border-t border-cream/10">
        <p className="text-xs uppercase tracking-wider text-cream/50 mb-3">Add new</p>
        <div className="grid sm:grid-cols-2 gap-4">{renderForm(form, set)}</div>
        <button type="submit" disabled={saving} className="btn-ghost mt-4 text-sm">
          <Plus className="w-4 h-4" />
          {saving ? 'Adding…' : 'Add'}
        </button>
      </form>

      {/* Move on to the next section. */}
      {onDone && (
        <div className="mt-6 pt-5 border-t border-cream/10 flex flex-wrap items-center justify-between gap-3">
          <p className="text-xs text-cream/50 max-w-sm">
            {items && items.length > 0
              ? 'Done with this section? You can come back and add more at any time.'
              : continueHint || 'This section is optional — you can skip it and add items later.'}
          </p>
          <button type="button" onClick={() => onDone()} className="btn-primary text-sm shrink-0">
            {items && items.length > 0 ? 'Save & continue' : 'Skip for now'}
            <ArrowRight className="w-4 h-4" />
          </button>
        </div>
      )}
    </SectionCard>
  );
}

/* Row header shared by sub-entities: title + type tag + optional verify badge */
function RowHead({ title, type, status, typeMap }) {
  const label = typeMap ? Object.fromEntries(typeMap)[type] || type : type;
  return (
    <div className="flex flex-wrap items-center gap-2">
      <span className="font-medium text-white truncate">{title}</span>
      {type && (
        <span className="tag bg-cream/5 text-cream/70 capitalize">
          {String(label).replace(/_/g, ' ')}
        </span>
      )}
      {status !== undefined && <VerifyBadge status={status} />}
    </div>
  );
}

/* ───────────────────────────── Projects tab ─────────────────────────────── */

function AssessmentTab({ profile, onSaved, onDone }) {
  const [text, setText] = useState(profile.profile_statement || '');
  const [saving, setSaving] = useState(false);
  const [failed, setFailed] = useState(false);
  const score = profile.profile_score || 0;

  const save = async () => {
    setSaving(true);
    try {
      const updated = await studentService.updateMe({ profile_statement: text });
      onSaved(updated);
      setFailed(false);
      toast.success('Profile assessment saved and scored.');
      onDone?.(updated?.field_slug);
    } catch (err) {
      // This save runs the AI scorer server-side and can time out. It is the
      // final section for profile-model students, so a failure here must not
      // trap them — surface an explicit way to move on.
      setFailed(true);
      toast.error(err?.response?.data?.error?.message || 'Could not save your assessment.');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="card p-6 space-y-4">
      <div>
        <h2 className="font-semibold flex items-center gap-2">
          <Sparkles className="w-4 h-4 text-gold-400" /> Achievements &amp; Profile Assessment
        </h2>
        <p className="text-sm text-cream/60 mt-1">
          For your field this is worth <span className="text-cream/90 font-medium">60 of your 100 points</span>.
          Describe your accomplishments in detail — an AI reads this text to score you.
        </p>
      </div>
      <div className="rounded-lg border border-gold-400/20 bg-gold-400/[0.05] px-3 py-2 text-xs text-cream/70 leading-relaxed">
        Include your leadership positions, internships &amp; work experience, volunteering, research,
        publications, certifications, competitions, awards, entrepreneurship, community impact, a
        personal statement, and any other relevant accomplishments.{' '}
        <span className="text-cream/90 font-medium">This information will be used during your evaluation</span>,
        so be specific and honest.
      </div>
      <textarea
        className="input min-h-[240px]"
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder="Describe your achievements and accomplishments…"
        maxLength={8000}
      />
      <div className="flex items-center justify-between gap-3 flex-wrap">
        <div className="text-sm">
          <span className="text-cream/60">Current assessment score: </span>
          <span className="font-display font-bold text-gold-400">
            {Math.round(score)}
            <span className="text-xs text-cream/40">/60</span>
          </span>
        </div>
        <div className="flex items-center gap-2 flex-wrap">
          {failed && (
            <button type="button" onClick={() => onDone?.()} className="btn-ghost text-sm">
              Continue anyway
              <ArrowRight className="w-4 h-4" />
            </button>
          )}
          <button onClick={save} disabled={saving} className="btn-primary">
            {saving ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" /> Saving &amp; scoring…
              </>
            ) : (
              <>
                Save &amp; finish
                <ArrowRight className="w-4 h-4" />
              </>
            )}
          </button>
        </div>
      </div>
      <p className="text-[11px] text-cream/40">{text.length}/8000 characters</p>
    </div>
  );
}

function ProjectsTab({ onChange, onDone, isMusic }) {
  return (
    <EntitySection
      onDone={onDone}
      continueHint={
        isMusic
          ? 'Your portfolio is AI-scored and worth 40 of your 100 points — adding at least one work is strongly recommended.'
          : 'Projects are AI-scored and worth 40 of your 100 points — adding at least one is strongly recommended.'
      }
      title={isMusic ? 'Portfolio' : 'Projects'}
      description={
        isMusic
          ? 'Add your music works — Spotify / Apple Music / SoundCloud releases, YouTube performances, compositions, videos and live shows. AI scores your portfolio (originality, production, reach, impact).'
          : 'Showcase work for AI rubric scoring (originality, depth, problem-solving, innovation).'
      }
      icon={isMusic ? Music : Lightbulb}
      onChange={onChange}
      load={studentService.listProjects}
      create={studentService.addProject}
      remove={studentService.removeProject}
      blankForm={{
        title: '',
        description: '',
        problem_statement: '',
        source_code_url: '',
        demo_video_url: '',
        report_url: '',
      }}
      renderRow={(it) => (
        <div>
          <RowHead title={it.title} status={it.status === 'pending' ? 'pending' : it.verification_status} />
          {it.description && (
            <p className="text-xs text-cream/55 mt-1 line-clamp-2">{it.description}</p>
          )}
          {it.final_score != null && (
            <p className="text-xs text-gold-300 mt-1 font-semibold">AI score: {it.final_score}</p>
          )}
        </div>
      )}
      extraRowAction={(it, refresh) => <EvaluateButton project={it} onDone={refresh} />}
      renderForm={(form, set) => (
        <>
          <Field label={isMusic ? 'Title / release' : 'Title'} full>
            <Text
              value={form.title}
              onChange={set('title')}
              placeholder={isMusic ? 'e.g. “Sunrise” (single)' : 'Project title'}
              required
            />
          </Field>
          <Field label={isMusic ? 'About this work' : 'Description'} full>
            <Area
              value={form.description}
              onChange={set('description')}
              placeholder={isMusic ? 'Genre, your role, the story…' : 'What does it do?'}
              required
            />
          </Field>
          <Field label={isMusic ? 'Notes (optional)' : 'Problem statement'} full>
            <Area
              value={form.problem_statement}
              onChange={set('problem_statement')}
              placeholder={isMusic ? 'Anything else worth noting.' : 'What problem does it solve?'}
              rows={2}
            />
          </Field>
          <Field label={isMusic ? 'Streaming link (Spotify / Apple / SoundCloud)' : 'Source code URL'}>
            <Text
              value={form.source_code_url}
              onChange={set('source_code_url')}
              placeholder={isMusic ? 'https://open.spotify.com/…' : 'https://github.com/…'}
            />
          </Field>
          <Field label={isMusic ? 'Video (YouTube / performance)' : 'Demo video URL'}>
            <Text value={form.demo_video_url} onChange={set('demo_video_url')} placeholder="https://…" />
          </Field>
          <Field label={isMusic ? 'Other portfolio link' : 'Report URL'} full>
            <Text
              value={form.report_url}
              onChange={set('report_url')}
              placeholder={isMusic ? 'https://… (portfolio / press)' : 'https://… (PDF or doc)'}
            />
          </Field>
        </>
      )}
    />
  );
}

function EvaluateButton({ project, onDone }) {
  const [busy, setBusy] = useState(false);
  const run = async () => {
    setBusy(true);
    try {
      await studentService.evaluateProject(project.id);
      toast.success('AI evaluation started.');
      onDone?.();
    } catch (err) {
      toast.error(err?.response?.data?.error?.message || 'Evaluation failed.');
    } finally {
      setBusy(false);
    }
  };
  return (
    <button
      onClick={run}
      disabled={busy}
      className="btn-ghost h-8 px-2 text-xs text-gold-300"
      title="Run AI evaluation"
    >
      {busy ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Sparkles className="w-3.5 h-3.5" />}
      <span className="hidden sm:inline">Evaluate</span>
    </button>
  );
}

/* ───────────────────────────── Research tab ─────────────────────────────── */

function ResearchTab({ onChange, onDone }) {
  return (
    <EntitySection
      onDone={onDone}
      title="Research"
      description="Publications, papers and research roles."
      icon={FlaskConical}
      onChange={onChange}
      load={studentService.listResearch}
      create={studentService.addResearch}
      remove={studentService.removeResearch}
      blankForm={{ type: 'journal_publication', title: '', venue: '', year: '', citations: '', doi: '', link: '', description: '' }}
      renderRow={(it) => (
        <div>
          <RowHead title={it.title} type={it.type} status={it.verification_status} typeMap={RESEARCH_TYPES} />
          <p className="text-xs text-cream/55 mt-1">
            {[it.venue, it.year].filter(Boolean).join(' · ')}
          </p>
        </div>
      )}
      renderForm={(form, set) => (
        <>
          <Field label="Type">
            <Select value={form.type} onChange={set('type')} options={RESEARCH_TYPES} />
          </Field>
          <Field label="Year">
            <Text type="number" value={form.year} onChange={set('year')} placeholder="2024" />
          </Field>
          <Field label="Title" full>
            <Text value={form.title} onChange={set('title')} placeholder="Title of the work" required />
          </Field>
          <Field label="Venue / Journal">
            <Text value={form.venue} onChange={set('venue')} placeholder="e.g. IEEE Access" />
          </Field>
          <Field label="Citations">
            <Text type="number" value={form.citations} onChange={set('citations')} placeholder="0" />
          </Field>
          <Field label="DOI">
            <Text value={form.doi} onChange={set('doi')} placeholder="10.xxxx/…" />
          </Field>
          <Field label="Link">
            <Text value={form.link} onChange={set('link')} placeholder="https://…" />
          </Field>
          <Field label="Description" full>
            <Area value={form.description} onChange={set('description')} rows={2} placeholder="Summary (optional)" />
          </Field>
        </>
      )}
    />
  );
}

/* ──────────────────────────── Experience tab ────────────────────────────── */

function ExperienceTab({ onChange, onDone }) {
  return (
    <EntitySection
      onDone={onDone}
      title="Experience"
      description="Internships, jobs, startups and volunteering."
      icon={Briefcase}
      onChange={onChange}
      load={studentService.listExperience}
      create={studentService.addExperience}
      remove={studentService.removeExperience}
      blankForm={{
        type: 'internship',
        organization: '',
        role_title: '',
        location: '',
        start_date: '',
        end_date: '',
        is_current: false,
        duration_months: '',
        description: '',
        link: '',
      }}
      renderRow={(it) => (
        <div>
          <RowHead title={it.organization} type={it.type} status={it.verification_status} typeMap={EXPERIENCE_TYPES} />
          <p className="text-xs text-cream/55 mt-1">
            {[it.role_title, it.location].filter(Boolean).join(' · ')}
            {it.is_current ? ' · Current' : ''}
          </p>
        </div>
      )}
      renderForm={(form, set) => (
        <>
          <Field label="Type">
            <Select value={form.type} onChange={set('type')} options={EXPERIENCE_TYPES} />
          </Field>
          <Field label="Organization">
            <Text value={form.organization} onChange={set('organization')} placeholder="Company / org" required />
          </Field>
          <Field label="Role title">
            <Text value={form.role_title} onChange={set('role_title')} placeholder="e.g. Software Intern" />
          </Field>
          <Field label="Location">
            <Text value={form.location} onChange={set('location')} placeholder="City, Country" />
          </Field>
          <Field label="Start date">
            <Text type="date" value={form.start_date} onChange={set('start_date')} />
          </Field>
          <Field label="End date">
            <Text type="date" value={form.end_date} onChange={set('end_date')} disabled={form.is_current} />
          </Field>
          <Field label="Duration (months)">
            <Text type="number" value={form.duration_months} onChange={set('duration_months')} placeholder="e.g. 6" />
          </Field>
          <Field label="Link">
            <Text value={form.link} onChange={set('link')} placeholder="https://…" />
          </Field>
          <div className="sm:col-span-2 flex items-center gap-2">
            <input
              id="is_current"
              type="checkbox"
              checked={form.is_current}
              onChange={(e) => set('is_current')(e.target.checked)}
              className="h-4 w-4 accent-gold-400"
            />
            <label htmlFor="is_current" className="text-sm text-cream/80">
              I currently work here
            </label>
          </div>
          <Field label="Description" full>
            <Area value={form.description} onChange={set('description')} rows={2} placeholder="What did you do?" />
          </Field>
        </>
      )}
    />
  );
}

/* ─────────────────────────── Competitions tab ───────────────────────────── */

function CompetitionsTab({ onChange, onDone }) {
  return (
    <EntitySection
      onDone={onDone}
      title="Competitions"
      description="Hackathons, debates, moot court and more."
      icon={Trophy}
      onChange={onChange}
      load={studentService.listCompetitions}
      create={studentService.addCompetition}
      remove={studentService.removeCompetition}
      blankForm={{ type: 'hackathon', result: 'participant', title: '', organizer: '', year: '', description: '', link: '' }}
      renderRow={(it) => (
        <div>
          <RowHead title={it.title} type={it.type} status={it.verification_status} typeMap={COMPETITION_TYPES} />
          <p className="text-xs text-cream/55 mt-1 capitalize">
            {[String(it.result || '').replace(/_/g, ' '), it.organizer, it.year].filter(Boolean).join(' · ')}
          </p>
        </div>
      )}
      renderForm={(form, set) => (
        <>
          <Field label="Type">
            <Select value={form.type} onChange={set('type')} options={COMPETITION_TYPES} />
          </Field>
          <Field label="Result">
            <Select value={form.result} onChange={set('result')} options={COMPETITION_RESULTS} />
          </Field>
          <Field label="Title" full>
            <Text value={form.title} onChange={set('title')} placeholder="Competition / award name" required />
          </Field>
          <Field label="Organizer">
            <Text value={form.organizer} onChange={set('organizer')} placeholder="Host organisation" />
          </Field>
          <Field label="Year">
            <Text type="number" value={form.year} onChange={set('year')} placeholder="2024" />
          </Field>
          <Field label="Link">
            <Text value={form.link} onChange={set('link')} placeholder="https://…" />
          </Field>
          <Field label="Description" full>
            <Area value={form.description} onChange={set('description')} rows={2} placeholder="Details (optional)" />
          </Field>
        </>
      )}
    />
  );
}

/* ──────────────────────────── Leadership tab ────────────────────────────── */

function LeadershipTab({ onChange, onDone }) {
  return (
    <EntitySection
      onDone={onDone}
      title="Leadership"
      description="Student leadership, community impact and professional orgs."
      icon={Users}
      onChange={onChange}
      load={studentService.listLeadership}
      create={studentService.addLeadership}
      remove={studentService.removeLeadership}
      blankForm={{ type: 'student_leadership', title: '', organization: '', role_title: '', start_date: '', end_date: '', description: '', link: '' }}
      renderRow={(it) => (
        <div>
          <RowHead title={it.title} type={it.type} status={it.verification_status} typeMap={LEADERSHIP_TYPES} />
          <p className="text-xs text-cream/55 mt-1">
            {[it.role_title, it.organization].filter(Boolean).join(' · ')}
          </p>
        </div>
      )}
      renderForm={(form, set) => (
        <>
          <Field label="Type">
            <Select value={form.type} onChange={set('type')} options={LEADERSHIP_TYPES} />
          </Field>
          <Field label="Title" full>
            <Text value={form.title} onChange={set('title')} placeholder="e.g. President, Robotics Club" required />
          </Field>
          <Field label="Organization">
            <Text value={form.organization} onChange={set('organization')} placeholder="Org / society" />
          </Field>
          <Field label="Role title">
            <Text value={form.role_title} onChange={set('role_title')} placeholder="e.g. President" />
          </Field>
          <Field label="Start date">
            <Text type="date" value={form.start_date} onChange={set('start_date')} />
          </Field>
          <Field label="End date">
            <Text type="date" value={form.end_date} onChange={set('end_date')} />
          </Field>
          <Field label="Description" full>
            <Area value={form.description} onChange={set('description')} rows={2} placeholder="What did you lead / achieve?" />
          </Field>
          <Field label="Link" full>
            <Text value={form.link} onChange={set('link')} placeholder="https://…" />
          </Field>
        </>
      )}
    />
  );
}

/* ─────────────────────────── Achievements tab ───────────────────────────── */

function AchievementsTab({ onChange, onDone }) {
  return (
    <EntitySection
      onDone={onDone}
      title="Achievements"
      description="Awards, certifications, scholarships and recognition. Attach evidence to get verified faster."
      icon={Award}
      onChange={onChange}
      load={studentService.listAchievements}
      create={studentService.addAchievement}
      remove={studentService.removeAchievement}
      blankForm={{ type: 'award', title: '', description: '', link: '', evidence: null }}
      renderRow={(it) => (
        <div>
          <RowHead title={it.title} type={it.type} status={it.verification_status} typeMap={ACHIEVEMENT_TYPES} />
          {it.description && <p className="text-xs text-cream/55 mt-1 line-clamp-2">{it.description}</p>}
        </div>
      )}
      renderForm={(form, set) => (
        <>
          <Field label="Type">
            <Select value={form.type} onChange={set('type')} options={ACHIEVEMENT_TYPES} />
          </Field>
          <Field label="Title">
            <Text value={form.title} onChange={set('title')} placeholder="Achievement title" required />
          </Field>
          <Field label="Description" full>
            <Area value={form.description} onChange={set('description')} rows={2} placeholder="Details (optional)" />
          </Field>
          <Field label="Link">
            <Text value={form.link} onChange={set('link')} placeholder="https://… (optional)" />
          </Field>
          <Field label="Evidence (file)">
            <input
              type="file"
              className="input file:mr-3 file:rounded-md file:border-0 file:bg-cream/10 file:px-3 file:py-1 file:text-xs file:text-white"
              onChange={(e) => set('evidence')(e.target.files?.[0] || null)}
            />
          </Field>
        </>
      )}
    />
  );
}
