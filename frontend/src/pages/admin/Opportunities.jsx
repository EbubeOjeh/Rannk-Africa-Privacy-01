import { useEffect, useState } from 'react';
import { Briefcase, Lock, Plus, Star, Trash2, Users, X } from 'lucide-react';
import toast from 'react-hot-toast';
import { adminService } from '@/services/admin.service';
import { Loader } from '@/components/Loader';
import { EmptyState } from '@/components/EmptyState';

// Mirrors the backend OpportunityType enum (app/models/opportunity.py). The
// value is what the API expects; the label is what admins see.
const TYPES = [
  ['internship', 'Internship'],
  ['graduate_job', 'Graduate Job'],
  ['scholarship', 'Scholarship'],
  ['research', 'Research'],
  ['competition', 'Competition'],
  ['leadership_program', 'Leadership Program'],
];

const emptyForm = {
  type: 'internship',
  title: '',
  description: '',
  organization: '',
  location: '',
  requirements: '',
  apply_url: '',
  deadline: '',
  min_score: '',
  is_featured: false,
};

export default function Opportunities() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(null);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState(emptyForm);
  const [creating, setCreating] = useState(false);
  const [applicantsFor, setApplicantsFor] = useState(null);
  const [applicants, setApplicants] = useState([]);
  const [applicantsLoading, setApplicantsLoading] = useState(false);

  const viewApplicants = async (opp) => {
    setApplicantsFor(opp);
    setApplicants([]);
    setApplicantsLoading(true);
    try {
      const data = await adminService.opportunityApplicants(opp.id);
      setApplicants(Array.isArray(data) ? data : []);
    } catch (err) {
      toast.error(err?.response?.data?.error?.message || 'Could not load applicants.');
    } finally {
      setApplicantsLoading(false);
    }
  };

  const load = () => {
    setLoading(true);
    adminService
      .adminOpportunities()
      .then((d) => setItems(Array.isArray(d) ? d : []))
      .catch(() => setItems([]))
      .finally(() => setLoading(false));
  };
  useEffect(load, []);

  const setField = (k, v) => setForm((f) => ({ ...f, [k]: v }));

  const create = async (e) => {
    e.preventDefault();
    setCreating(true);
    try {
      const payload = { ...form };
      if (payload.min_score === '') delete payload.min_score;
      else payload.min_score = Number(payload.min_score);
      Object.keys(payload).forEach((k) => {
        if (payload[k] === '') delete payload[k];
      });
      await adminService.createOpportunity(payload);
      toast.success('Opportunity posted.');
      setForm(emptyForm);
      setShowForm(false);
      load();
    } catch (err) {
      toast.error(err?.response?.data?.error?.message || 'Could not post opportunity.');
    } finally {
      setCreating(false);
    }
  };

  const close = async (opp) => {
    setBusy(opp.id);
    try {
      await adminService.closeOpportunity(opp.id);
      toast.success('Opportunity closed.');
      load();
    } catch (err) {
      toast.error(err?.response?.data?.error?.message || 'Action failed.');
    } finally {
      setBusy(null);
    }
  };

  const remove = async (opp) => {
    if (!confirm(`Delete “${opp.title}”? This cannot be undone.`)) return;
    setBusy(opp.id);
    try {
      await adminService.deleteOpportunity(opp.id);
      toast.success('Opportunity deleted.');
      setItems((prev) => prev.filter((o) => o.id !== opp.id));
    } catch (err) {
      toast.error(err?.response?.data?.error?.message || 'Delete failed.');
    } finally {
      setBusy(null);
    }
  };

  return (
    <div>
      <div className="flex items-start justify-between gap-4">
        <div>
          <h1 className="font-display text-2xl font-bold flex items-center gap-2">
            <Briefcase className="w-6 h-6 text-gold-400" /> Opportunities
          </h1>
          <p className="text-sm text-cream/60 mt-1">
            Manage every opportunity — active and closed. Post new internships, jobs, scholarships and more.
          </p>
        </div>
        <button onClick={() => setShowForm((s) => !s)} className="btn-primary shrink-0">
          {showForm ? <X className="w-4 h-4" /> : <Plus className="w-4 h-4" />}
          {showForm ? 'Cancel' : 'Post opportunity'}
        </button>
      </div>

      {showForm && (
        <form onSubmit={create} className="card p-6 mt-6 space-y-3">
          <h2 className="font-semibold flex items-center gap-2">
            <Plus className="w-4 h-4 text-gold-400" /> New opportunity
          </h2>
          <div className="grid sm:grid-cols-2 gap-3">
            <label className="block">
              <span className="field-label">Type</span>
              <select className="input" value={form.type} onChange={(e) => setField('type', e.target.value)}>
                {TYPES.map(([value, label]) => (
                  <option key={value} value={value}>
                    {label}
                  </option>
                ))}
              </select>
            </label>
            <Field label="Title" required value={form.title} onChange={(v) => setField('title', v)} />
            <Field label="Organization / Sponsor" value={form.organization} onChange={(v) => setField('organization', v)} />
            <Field label="Location" value={form.location} onChange={(v) => setField('location', v)} />
            <Field label="Apply URL" type="url" value={form.apply_url} onChange={(v) => setField('apply_url', v)} />
            <Field label="Deadline" type="date" value={form.deadline} onChange={(v) => setField('deadline', v)} />
            <Field label="Min score (optional)" type="number" value={form.min_score} onChange={(v) => setField('min_score', v)} />
          </div>
          <label className="block">
            <span className="field-label">
              Description <span className="text-gold-400">*</span>
            </span>
            <textarea
              className="input min-h-[80px]"
              value={form.description}
              onChange={(e) => setField('description', e.target.value)}
              placeholder="At least 10 characters."
              required
              minLength={10}
            />
          </label>
          <label className="block">
            <span className="field-label">Requirements / Eligibility</span>
            <textarea
              className="input min-h-[60px]"
              value={form.requirements}
              onChange={(e) => setField('requirements', e.target.value)}
              placeholder="e.g. Open to students based in Abuja."
            />
          </label>
          <label className="flex items-center gap-2 text-sm text-cream/80">
            <input
              type="checkbox"
              checked={form.is_featured}
              onChange={(e) => setField('is_featured', e.target.checked)}
              className="accent-gold-400 w-4 h-4"
            />
            Feature this opportunity
          </label>
          <div className="flex justify-end">
            <button
              type="submit"
              disabled={creating || !form.title.trim() || form.description.trim().length < 10}
              className="btn-primary"
            >
              <Plus className="w-4 h-4" /> {creating ? 'Posting…' : 'Post opportunity'}
            </button>
          </div>
        </form>
      )}

      <div className="card mt-6 overflow-x-auto">
        <div className="data-head">
          <div className="col-span-4">Title</div>
          <div className="col-span-2">Type</div>
          <div className="col-span-3">Organization</div>
          <div className="col-span-1">Status</div>
          <div className="col-span-2 text-right">Actions</div>
        </div>
        {loading ? (
          <Loader />
        ) : items.length === 0 ? (
          <EmptyState
            icon={Briefcase}
            title="No opportunities yet"
            description="Post the first internship, job or scholarship for students."
          />
        ) : (
          items.map((o) => (
            <div key={o.id} className="data-row">
              <div className="col-span-4 min-w-0">
                <div className="font-medium truncate flex items-center gap-1.5">
                  {o.is_featured && <Star className="w-3.5 h-3.5 text-gold-400 shrink-0" fill="currentColor" />}
                  {o.title}
                </div>
                <div className="text-[11px] text-cream/40 truncate">
                  {o.created_at ? new Date(o.created_at).toLocaleDateString() : ''}
                </div>
              </div>
              <div className="col-span-2 text-sm text-cream/70 truncate capitalize">{o.type || '—'}</div>
              <div className="col-span-3 text-sm text-cream/70 truncate">{o.organization || '—'}</div>
              <div className="col-span-1">
                <span className={o.is_active ? 'pill-success' : 'pill bg-cream/10 text-cream/60'}>
                  {o.is_active ? 'Active' : 'Closed'}
                </span>
              </div>
              <div className="col-span-2 flex justify-end gap-1">
                <button
                  onClick={() => viewApplicants(o)}
                  className="btn-ghost h-8 px-2 text-xs"
                  title="View applicants"
                >
                  <Users className="w-3.5 h-3.5" /> Applicants
                </button>
                {o.is_active && (
                  <button
                    disabled={busy === o.id}
                    onClick={() => close(o)}
                    className="btn-ghost h-8 px-2 text-xs text-amber-200"
                    title="Close opportunity"
                  >
                    <Lock className="w-3.5 h-3.5" /> Close
                  </button>
                )}
                <button
                  disabled={busy === o.id}
                  onClick={() => remove(o)}
                  className="btn-ghost h-8 w-8 p-0 text-rose-300"
                  title="Delete opportunity"
                >
                  <Trash2 className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          ))
        )}
      </div>

      {applicantsFor && (
        <ApplicantsModal
          opportunity={applicantsFor}
          applicants={applicants}
          loading={applicantsLoading}
          onClose={() => setApplicantsFor(null)}
        />
      )}
    </div>
  );
}

function ApplicantsModal({ opportunity, applicants, loading, onClose }) {
  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm"
      onClick={onClose}
    >
      <div
        className="card w-full max-w-2xl max-h-[85vh] flex flex-col p-0"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between gap-3 p-5 border-b border-cream/10">
          <div className="min-w-0">
            <h2 className="font-semibold truncate flex items-center gap-2">
              <Users className="w-4 h-4 text-gold-400" /> Applicants — {opportunity.title}
            </h2>
            <p className="text-xs text-cream/50 mt-0.5">
              {applicants.length} applicant{applicants.length === 1 ? '' : 's'}
            </p>
          </div>
          <button onClick={onClose} className="btn-ghost h-9 w-9 p-0" aria-label="Close">
            <X className="w-5 h-5" />
          </button>
        </div>
        <div className="p-5 overflow-y-auto">
          {loading ? (
            <Loader />
          ) : applicants.length === 0 ? (
            <EmptyState
              icon={Users}
              title="No applicants yet"
              description="Students who apply to this opportunity will appear here."
            />
          ) : (
            <div className="space-y-2">
              {applicants.map((a) => (
                <div
                  key={a.application_id}
                  className="flex items-center gap-3 rounded-lg border border-cream/10 px-3 py-2"
                >
                  <div className="w-9 h-9 rounded-full bg-cream/10 overflow-hidden shrink-0 grid place-content-center text-xs text-cream/60">
                    {a.avatar_url ? (
                      <img src={a.avatar_url} alt="" className="w-full h-full object-cover" />
                    ) : (
                      (a.full_name || '?').slice(0, 1).toUpperCase()
                    )}
                  </div>
                  <div className="min-w-0 flex-1">
                    <div className="font-medium text-sm truncate">{a.full_name}</div>
                    <div className="text-[11px] text-cream/50 truncate">
                      {[a.field_name, a.university_name].filter(Boolean).join(' · ') || '—'}
                    </div>
                    {(a.email || a.linkedin_url) && (
                      <div className="text-[11px] text-cream/50 truncate">
                        {a.email}
                        {a.email && a.linkedin_url ? ' · ' : ''}
                        {a.linkedin_url && (
                          <a
                            href={a.linkedin_url}
                            target="_blank"
                            rel="noreferrer"
                            className="text-gold-300 hover:underline"
                          >
                            LinkedIn
                          </a>
                        )}
                      </div>
                    )}
                  </div>
                  <div className="text-right shrink-0">
                    <div className="font-display font-bold text-gold-400">
                      {Math.round(a.final_score || 0)}
                      <span className="text-[10px] text-cream/40">/100</span>
                    </div>
                    {a.overall_rank && <div className="text-[10px] text-cream/40">#{a.overall_rank}</div>}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function Field({ label, value, onChange, type = 'text', required }) {
  return (
    <label className="block">
      <span className="field-label">
        {label} {required && <span className="text-gold-400">*</span>}
      </span>
      <input
        type={type}
        className="input"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        required={required}
      />
    </label>
  );
}
