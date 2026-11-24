import ApplicationReview from '@/components/ApplicationReview';
import { api } from '@/services/api';
import { useEffect, useMemo, useState } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import { Link } from 'react-router-dom';
import {
  Briefcase,
  MapPin,
  Calendar,
  ExternalLink,
  Filter,
  Sparkles,
  Building2,
  Star,
  Send,
  CheckCircle2,
  AlertCircle,
} from 'lucide-react';
import { FieldChip } from '@/components/FieldChip';
import { Loader } from '@/components/Loader';
import { EmptyState } from '@/components/EmptyState';
import { EditableSection } from '@/components/EditableSection';
import { BackLink } from '@/components/BackLink';
import { PageGuide } from '@/components/PageGuide';
import { useAuth } from '@/hooks/useAuth';
import { usePageContent } from '@/hooks/usePageContent';
import { opportunitiesService } from '@/services/opportunities.service';
import { studentService } from '@/services/student.service';
import { fieldsService } from '@/services/fields.service';

// Mirror of the API enum (kept local — the public page can't import admin consts).
const OPPORTUNITY_TYPES = [
  { value: 'internship', label: 'Internship' },
  { value: 'graduate_job', label: 'Graduate Job' },
  { value: 'scholarship', label: 'Scholarship' },
  { value: 'research', label: 'Research' },
  { value: 'competition', label: 'Competition' },
  { value: 'leadership_program', label: 'Leadership Program' },
];
const typeLabel = (t) =>
  OPPORTUNITY_TYPES.find((o) => o.value === t)?.label || (t || '').replace(/_/g, ' ');

export default function OpportunityPortal() {
  const { isAuthenticated, role } = useAuth();
  const isStudent = isAuthenticated && role === 'student';
  const c = usePageContent('opportunities');

  const [opps, setOpps] = useState([]);
  const [fields, setFields] = useState([]);
  const [recs, setRecs] = useState({}); // opportunity_id → { score, reasoning }
  const [loading, setLoading] = useState(true);

  const [type, setType] = useState('');
  const [fieldId, setFieldId] = useState('');

  // Apply flow.
  const [appliedIds, setAppliedIds] = useState(new Set());
  const [studentFieldId, setStudentFieldId] = useState(null);
  const [applyingId, setApplyingId] = useState(null);
  const [review,setReview] = useState(null);
  const [popup, setPopup] = useState(null); // { kind, message? }

  useEffect(() => {
    fieldsService.list().then(setFields).catch(() => setFields([]));
  }, []);

  // Student-only: AI recommendations, already-applied set, and the student's
  // field (to surface same-field opportunities first as "Recommended").
  useEffect(() => {
    if (!isStudent) {
      setRecs({});
      setAppliedIds(new Set());
      setStudentFieldId(null);
      return;
    }
    opportunitiesService
      .recommended()
      .then((list) => {
        const map = {};
        (Array.isArray(list) ? list : []).forEach((r) => {
          const oid = r.opportunity?.id;
          if (oid != null) map[oid] = { score: r.score, reasoning: r.reasoning };
        });
        setRecs(map);
      })
      .catch(() => setRecs({}));
    opportunitiesService
      .myApplications()
      .then((list) =>
        setAppliedIds(new Set((Array.isArray(list) ? list : []).map((a) => a.opportunity_id))),
      )
      .catch(() => setAppliedIds(new Set()));
    studentService
      .me()
      .then((me) => setStudentFieldId(me?.field_id ?? null))
      .catch(() => setStudentFieldId(null));
  }, [isStudent]);

  useEffect(() => {
    setLoading(true);
    const params = { active_only: true };
    if (type) params.type = type;
    if (fieldId) params.field_id = fieldId;
    opportunitiesService
      .list(params)
      .then((data) => setOpps(Array.isArray(data) ? data : []))
      .catch(() => setOpps([]))
      .finally(() => setLoading(false));
  }, [type, fieldId]);

  // Recommended-first: same-field opportunities float to the top for a signed-in
  // student, then by AI match score.
  const ordered = useMemo(() => {
    if (!isStudent) return opps;
    const rank = (o) =>
      (studentFieldId && o.field_id === studentFieldId ? 1_000_000 : 0) + (recs[o.id]?.score ?? 0);
    return [...opps].sort((a, b) => rank(b) - rank(a));
  }, [opps, recs, isStudent, studentFieldId]);

  const handleApply = async (opp) => {
    if (!isStudent) {
      setPopup({ kind: 'signin' });
      return;
    }
    if (appliedIds.has(opp.id)) return;
    setApplyingId(opp.id);
    try {
      const res = await api.get(`/privacy/opportunities/${opp.id}/review`);
      setReview(res.data);
    } catch (err) {
      const message =
        err?.response?.data?.detail || err?.response?.data?.error?.message || 'Could not submit your application. Please try again.';
      const incomplete = /profile/i.test(message);
      setPopup({ kind: incomplete ? 'incomplete' : 'error', message });
    } finally {
      setApplyingId(null);
    }
  };

  return (
    <section className="container-page py-12">
      <BackLink className="mb-5" />
      <PageGuide
        id="opportunities"
        className="mb-6"
        title="Roles, scholarships and competitions open to students"
        steps={[
          'Browse everything posted by recruiters and by Rank Africa. Use the filters to narrow by type or field.',
          'Open a listing to read the full brief and the eligibility requirements.',
          'Discovery sharing is optional. Review the named recipient and required fields before applying; all optional application fields can remain unchecked.',
        ]}
        cta={{ to: '/student-register', label: 'Create a profile to apply' }}
      />
      <EditableSection page="opportunities" id="header" title="Header">
        <motion.div initial={{ opacity: 0, y: 6 }} animate={{ opacity: 1, y: 0 }}>
          <p className="text-xs uppercase tracking-wider text-cream/50">{c.header.eyebrow}</p>
          <h1 className="font-display text-3xl sm:text-4xl font-extrabold mt-1 flex items-center gap-3">
            <Briefcase className="w-7 h-7 text-gold-400" /> {c.header.heading}
          </h1>
          <p className="text-sm text-cream/60 mt-2 max-w-2xl">
            {c.header.intro}
            {isStudent && ' Opportunities matched to your field appear first.'}
          </p>
        </motion.div>
      </EditableSection>

      {/* Filters */}
      <div className="flex flex-col sm:flex-row sm:flex-wrap gap-3 mt-8">
        <Select label="Type" value={type} onChange={setType}>
          <option value="">All types</option>
          {OPPORTUNITY_TYPES.map((t) => (
            <option key={t.value} value={t.value}>
              {t.label}
            </option>
          ))}
        </Select>
        <Select label="Field" value={fieldId} onChange={setFieldId}>
          <option value="">All fields</option>
          {fields.map((f) => (
            <option key={f.id} value={f.id}>
              {f.name}
            </option>
          ))}
        </Select>
      </div>

      {/* List */}
      <div className="mt-8">
        {loading ? (
          <Loader label="Loading opportunities…" />
        ) : ordered.length === 0 ? (
          <EmptyState
            title="No opportunities right now"
            description="Check back soon — new roles and scholarships are posted regularly."
            icon={Briefcase}
          />
        ) : (
          <div className="grid md:grid-cols-2 gap-4">
            {ordered.map((opp, i) => (
              <OpportunityCard
                key={opp.id}
                opp={opp}
                rec={recs[opp.id]}
                index={i}
                recommended={isStudent && !!studentFieldId && opp.field_id === studentFieldId}
                applied={appliedIds.has(opp.id)}
                applying={applyingId === opp.id}
                onApply={handleApply}
              />
            ))}
          </div>
        )}
      </div>

      {review && <ApplicationReview key={review.opportunity_id} review={review} onClose={()=>setReview(null)} onSubmitted={res=>{setAppliedIds(prev=>new Set(prev).add(review.opportunity_id));setReview(null);setPopup({kind:res.already_applied?'already':'success'});}} />}
      <ApplyPopup popup={popup} onClose={() => setPopup(null)} />
    </section>
  );
}

function OpportunityCard({ opp, rec, index, recommended, applied, applying, onApply }) {
  const matchPct =
    rec?.score != null
      ? Math.round(rec.score <= 1 ? rec.score * 100 : rec.score) // tolerate 0–1 or 0–100
      : null;

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: Math.min(index * 0.04, 0.4) }}
      className="card p-5 flex flex-col gap-3"
    >
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <div className="flex items-center gap-2 flex-wrap">
            <span className="tag bg-gold-400/15 text-gold-300">{typeLabel(opp.type)}</span>
            {opp.field_name && <FieldChip name={opp.field_name} slug={opp.field_name} />}
          </div>
          <h3 className="font-semibold text-white mt-2">{opp.title}</h3>
          {opp.organization && (
            <div className="text-xs text-cream/60 mt-0.5 inline-flex items-center gap-1">
              <Building2 className="w-3 h-3" /> {opp.organization}
            </div>
          )}
        </div>
        <div className="flex flex-col items-end gap-1 shrink-0">
          {recommended && (
            <span className="pill bg-gold-400/15 text-gold-300">
              <Star className="w-3 h-3" /> Recommended
            </span>
          )}
          {matchPct != null && (
            <span className="pill bg-emerald-500/15 text-emerald-300">
              <Sparkles className="w-3 h-3" /> {matchPct}% Match
            </span>
          )}
        </div>
      </div>

      {opp.description && <p className="text-sm text-cream/70 line-clamp-3">{opp.description}</p>}

      {rec?.reasoning && (
        <div className="rounded-lg border border-emerald-400/20 bg-emerald-500/[0.06] px-3 py-2 text-xs text-emerald-100/80">
          <span className="font-semibold text-emerald-300">Why you match: </span>
          {rec.reasoning}
        </div>
      )}

      {opp.requirements && (
        <p className="text-xs text-cream/50">
          <span className="font-medium text-cream/70">Requirements: </span>
          {opp.requirements}
        </p>
      )}

      <div className="flex items-center gap-3 text-xs text-cream/50 flex-wrap">
        {opp.location && (
          <span className="inline-flex items-center gap-1">
            <MapPin className="w-3 h-3" /> {opp.location}
          </span>
        )}
        {opp.deadline && (
          <span className="inline-flex items-center gap-1">
            <Calendar className="w-3 h-3" /> Closes {new Date(opp.deadline).toLocaleDateString()}
          </span>
        )}
        {(opp.min_score != null || opp.min_gpa != null) && (
          <span>
            Min{' '}
            {opp.min_score != null
              ? `${opp.min_score}/100`
              : `${Number(opp.min_gpa).toFixed(2)} GPA`}
          </span>
        )}
      </div>

      <div className="pt-1 flex items-center gap-3 flex-wrap">
        <button
          type="button"
          onClick={() => onApply(opp)}
          disabled={applied || applying}
          className={`btn-primary text-xs ${applied ? 'opacity-70 cursor-default' : ''}`}
        >
          {applied ? (
            <>
              <CheckCircle2 className="w-3.5 h-3.5" /> Applied
            </>
          ) : applying ? (
            'Applying…'
          ) : (
            <>
              Apply <Send className="w-3.5 h-3.5" />
            </>
          )}
        </button>
        {opp.apply_url && (
          <a
            href={opp.apply_url}
            target="_blank"
            rel="noopener noreferrer"
            className="text-xs text-cream/60 hover:text-gold-300 inline-flex items-center gap-1"
          >
            View posting <ExternalLink className="w-3 h-3" />
          </a>
        )}
      </div>
    </motion.div>
  );
}

function ApplyPopup({ popup, onClose }) {
  const config = {
    success: {
      icon: CheckCircle2,
      tone: 'text-emerald-400 bg-emerald-500/15',
      title: 'Application received',
      body: "Your application has been received. We'll notify you if you're selected.",
      cta: null,
    },
    already: {
      icon: CheckCircle2,
      tone: 'text-emerald-400 bg-emerald-500/15',
      title: "You've already applied",
      body: "Your application has been received. We'll notify you if you're selected.",
      cta: null,
    },
    incomplete: {
      icon: AlertCircle,
      tone: 'text-gold-400 bg-gold-400/15',
      title: 'Complete your profile first',
      body: 'Please complete your RankAfrica profile before applying to opportunities.',
      cta: { to: '/student/profile', label: 'Complete my profile' },
    },
    signin: {
      icon: AlertCircle,
      tone: 'text-gold-400 bg-gold-400/15',
      title: 'Sign in to apply',
      body: 'Create a student profile or sign in to apply to opportunities.',
      cta: { to: '/student-register', label: 'Create your profile' },
    },
    error: {
      icon: AlertCircle,
      tone: 'text-red-400 bg-red-500/15',
      title: 'Could not apply',
      body: 'Something went wrong. Please try again.',
      cta: null,
    },
  };
  const cfg = popup ? config[popup.kind] : null;
  return (
    <AnimatePresence>
      {cfg && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm"
          onClick={onClose}
        >
          <motion.div
            initial={{ opacity: 0, scale: 0.94, y: 12 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.94, y: 12 }}
            transition={{ duration: 0.2 }}
            className="card w-full max-w-md p-7 text-center"
            onClick={(e) => e.stopPropagation()}
          >
            <div className={`w-12 h-12 mx-auto rounded-xl grid place-content-center ${cfg.tone}`}>
              <cfg.icon className="w-6 h-6" />
            </div>
            <h2 className="mt-4 font-display text-xl font-bold">{cfg.title}</h2>
            <p className="mt-3 text-sm text-cream/75 leading-relaxed">
              {popup?.message && (popup.kind === 'error' || popup.kind === 'incomplete')
                ? popup.message
                : cfg.body}
            </p>
            <div className="mt-6 flex flex-col gap-2">
              {cfg.cta && (
                <Link to={cfg.cta.to} className="btn-primary w-full justify-center">
                  {cfg.cta.label}
                </Link>
              )}
              <button onClick={onClose} className="btn-ghost w-full justify-center">
                {cfg.cta ? 'Not now' : 'Close'}
              </button>
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}

function Select({ label, value, onChange, children }) {
  return (
    <div className="relative w-full sm:w-auto">
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="input pr-8 appearance-none cursor-pointer"
        title={label}
      >
        {children}
      </select>
      <Filter className="w-3.5 h-3.5 absolute right-2 top-1/2 -translate-y-1/2 text-cream/40 pointer-events-none" />
    </div>
  );
}
