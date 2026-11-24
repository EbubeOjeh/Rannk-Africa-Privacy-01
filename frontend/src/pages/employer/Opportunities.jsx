import { useEffect, useState } from 'react';
import {
  Briefcase,
  Plus,
  Pencil,
  Trash2,
  Lock,
  X,
  MapPin,
  Calendar,
  Star,
} from 'lucide-react';
import toast from 'react-hot-toast';
import { Loader } from '@/components/Loader';
import { EmptyState } from '@/components/EmptyState';
import { FieldChip } from '@/components/FieldChip';
import { PageGuide } from '@/components/PageGuide';
import { useAuth } from '@/hooks/useAuth';
import { opportunitiesService } from '@/services/opportunities.service';
import { fieldsService } from '@/services/fields.service';

// type ∈ internship | graduate_job | scholarship | research | competition | leadership_program
export const OPPORTUNITY_TYPES = [
  { value: 'internship', label: 'Internship' },
  { value: 'graduate_job', label: 'Graduate Job' },
  { value: 'scholarship', label: 'Scholarship' },
  { value: 'research', label: 'Research' },
  { value: 'competition', label: 'Competition' },
  { value: 'leadership_program', label: 'Leadership Program' },
];

export const typeLabel = (t) =>
  OPPORTUNITY_TYPES.find((o) => o.value === t)?.label || (t || '').replace(/_/g, ' ');

const EMPTY_FORM = {
  type: 'internship',
  title: '',
  organization: '',
  description: '',
  location: '',
  requirements: '',
  apply_url: '',
  deadline: '',
  field_id: '',
  min_gpa: '',
  min_score: '',
  graduation_year: '',
  is_featured: false,
};

export default function EmployerOpportunities() {
  const { user } = useAuth();
  const approved = user?.approval_status === 'approved';

  const [items, setItems] = useState([]);
  const [fields, setFields] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editing, setEditing] = useState(null); // opportunity being edited, or null for create

  const refresh = () => {
    setLoading(true);
    opportunitiesService
      .list()
      .then((data) => {
        const all = Array.isArray(data) ? data : [];
        setItems(all.filter((o) => o.posted_by_id === user?.id));
      })
      .catch(() => setItems([]))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fieldsService.list().then(setFields).catch(() => setFields([]));
    refresh();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [user?.id]);

  const openCreate = () => {
    setEditing(null);
    setShowForm(true);
  };
  const openEdit = (opp) => {
    setEditing(opp);
    setShowForm(true);
  };
  const onSaved = () => {
    setShowForm(false);
    setEditing(null);
    refresh();
  };

  const close = async (opp) => {
    if (!confirm(`Close "${opp.title}"? It will no longer accept applicants.`)) return;
    try {
      await opportunitiesService.close(opp.id);
      toast.success('Opportunity closed.');
      refresh();
    } catch (err) {
      toast.error(err?.response?.data?.error?.message || 'Could not close.');
    }
  };

  const remove = async (opp) => {
    if (!confirm(`Delete "${opp.title}"? This cannot be undone.`)) return;
    try {
      await opportunitiesService.remove(opp.id);
      toast.success('Opportunity deleted.');
      refresh();
    } catch (err) {
      toast.error(err?.response?.data?.error?.message || 'Could not delete.');
    }
  };

  return (
    <div>
      <PageGuide
        id="employer-opportunities"
        className="mb-6"
        title="Posting opportunities"
        steps={[
          'Anything you post appears on the public Opportunities page for ranked students to apply to.',
          'Include the eligibility requirements — students review the recipient and fields before applying.',
          'Applications arrive against the listing; close it when the role is filled.',
        ]}
      />
      <div className="flex items-end justify-between gap-3 flex-wrap">
        <div>
          <p className="text-xs uppercase tracking-wider text-cream/50">Postings</p>
          <h1 className="font-display text-2xl sm:text-3xl font-bold mt-1 flex items-center gap-2">
            <Briefcase className="w-5 h-5 text-gold-400" /> My opportunities
          </h1>
          <p className="text-sm text-cream/60 mt-2">
            Post internships, jobs, scholarships and more to RankAfrica students.
          </p>
        </div>
        <button onClick={openCreate} disabled={!approved} className="btn-primary text-sm" title={!approved ? 'Available after approval' : undefined}>
          {approved ? <Plus className="w-4 h-4" /> : <Lock className="w-4 h-4" />} New opportunity
        </button>
      </div>

      {!approved && (
        <div className="mt-6 rounded-xl border border-amber-400/30 bg-amber-500/10 px-4 py-3 text-sm text-amber-100/90">
          Posting opportunities unlocks after a RankAfrica admin approves your account.
        </div>
      )}

      <div className="mt-6">
        {loading ? (
          <Loader label="Loading your opportunities…" />
        ) : items.length === 0 ? (
          <EmptyState
            title="No opportunities yet"
            description="Create your first posting to reach ranked students."
            icon={Briefcase}
            action={
              approved && (
                <button onClick={openCreate} className="btn-primary text-sm">
                  <Plus className="w-4 h-4" /> New opportunity
                </button>
              )
            }
          />
        ) : (
          <div className="space-y-3">
            {items.map((opp) => (
              <div key={opp.id} className="card p-5 flex items-start justify-between gap-4 flex-wrap">
                <div className="min-w-0 flex-1">
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className="font-semibold text-white">{opp.title}</span>
                    <span className="tag bg-cream/10 text-cream/70">{typeLabel(opp.type)}</span>
                    {opp.field_name && <FieldChip name={opp.field_name} slug={opp.field_name} />}
                    {opp.is_featured && (
                      <span className="pill bg-gold-400/15 text-gold-300">
                        <Star className="w-3 h-3" /> Featured
                      </span>
                    )}
                    <span className={opp.is_active ? 'pill-success' : 'pill bg-cream/10 text-cream/50'}>
                      {opp.is_active ? 'Active' : 'Closed'}
                    </span>
                  </div>
                  <div className="flex items-center gap-3 text-xs text-cream/50 mt-2 flex-wrap">
                    {opp.organization && <span>{opp.organization}</span>}
                    {opp.location && (
                      <span className="inline-flex items-center gap-1">
                        <MapPin className="w-3 h-3" /> {opp.location}
                      </span>
                    )}
                    {opp.deadline && (
                      <span className="inline-flex items-center gap-1">
                        <Calendar className="w-3 h-3" /> {new Date(opp.deadline).toLocaleDateString()}
                      </span>
                    )}
                  </div>
                  {opp.description && (
                    <p className="text-sm text-cream/70 mt-2 line-clamp-2">{opp.description}</p>
                  )}
                </div>
                <div className="flex items-center gap-1 shrink-0">
                  <button onClick={() => openEdit(opp)} className="btn-ghost text-xs" title="Edit">
                    <Pencil className="w-3.5 h-3.5" /> Edit
                  </button>
                  {opp.is_active && (
                    <button onClick={() => close(opp)} className="btn-ghost text-xs" title="Close">
                      <Lock className="w-3.5 h-3.5" /> Close
                    </button>
                  )}
                  <button onClick={() => remove(opp)} className="btn-ghost text-xs text-rose-300" title="Delete">
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {showForm && (
        <OpportunityFormModal
          fields={fields}
          editing={editing}
          onClose={() => setShowForm(false)}
          onSaved={onSaved}
        />
      )}
    </div>
  );
}

function OpportunityFormModal({ fields, editing, onClose, onSaved }) {
  const [form, setForm] = useState(() => {
    if (!editing) return EMPTY_FORM;
    return {
      type: editing.type || 'internship',
      title: editing.title || '',
      organization: editing.organization || '',
      description: editing.description || '',
      location: editing.location || '',
      requirements: editing.requirements || '',
      apply_url: editing.apply_url || '',
      // <input type=date> wants YYYY-MM-DD.
      deadline: editing.deadline ? String(editing.deadline).slice(0, 10) : '',
      field_id: editing.field_id ?? '',
      min_gpa: editing.min_gpa ?? '',
      min_score: editing.min_score ?? '',
      graduation_year: editing.graduation_year ?? '',
      is_featured: Boolean(editing.is_featured),
    };
  });
  const [saving, setSaving] = useState(false);

  const set = (k) => (e) =>
    setForm((f) => ({ ...f, [k]: e.target.type === 'checkbox' ? e.target.checked : e.target.value }));

  const submit = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      const payload = {
        type: form.type,
        title: form.title,
        description: form.description,
        is_featured: form.is_featured,
      };
      // Optional fields: only send when filled; coerce numerics.
      if (form.organization) payload.organization = form.organization;
      if (form.location) payload.location = form.location;
      if (form.requirements) payload.requirements = form.requirements;
      if (form.apply_url) payload.apply_url = form.apply_url;
      if (form.deadline) payload.deadline = form.deadline;
      if (form.field_id !== '') payload.field_id = form.field_id;
      if (form.min_gpa !== '') payload.min_gpa = Number(form.min_gpa);
      if (form.min_score !== '') payload.min_score = Number(form.min_score);
      if (form.graduation_year !== '') payload.graduation_year = Number(form.graduation_year);

      if (editing) {
        await opportunitiesService.update(editing.id, payload);
        toast.success('Opportunity updated.');
      } else {
        await opportunitiesService.create(payload);
        toast.success('Opportunity posted.');
      }
      onSaved();
    } catch (err) {
      toast.error(err?.response?.data?.error?.message || 'Could not save opportunity.');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center overflow-y-auto p-4">
      <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" onClick={onClose} />
      <div className="relative card p-6 w-full max-w-2xl my-8">
        <div className="flex items-center justify-between mb-4">
          <h2 className="font-display text-lg font-bold">
            {editing ? 'Edit opportunity' : 'New opportunity'}
          </h2>
          <button onClick={onClose} className="btn-ghost h-9 w-9 p-0" aria-label="Close">
            <X className="w-5 h-5" />
          </button>
        </div>

        <form onSubmit={submit} className="space-y-4">
          <div className="grid sm:grid-cols-2 gap-4">
            <Field label="Type" required>
              <select className="input" value={form.type} onChange={set('type')} required>
                {OPPORTUNITY_TYPES.map((t) => (
                  <option key={t.value} value={t.value}>
                    {t.label}
                  </option>
                ))}
              </select>
            </Field>
            <Field label="Organization">
              <input className="input" value={form.organization} onChange={set('organization')} />
            </Field>
          </div>

          <Field label="Title" required>
            <input className="input" value={form.title} onChange={set('title')} required />
          </Field>

          <Field label="Description" required>
            <textarea
              className="input min-h-[110px] resize-y"
              value={form.description}
              onChange={set('description')}
              required
            />
          </Field>

          <div className="grid sm:grid-cols-2 gap-4">
            <Field label="Location">
              <input className="input" value={form.location} onChange={set('location')} placeholder="Remote / Lagos" />
            </Field>
            <Field label="Application deadline">
              <input className="input" type="date" value={form.deadline} onChange={set('deadline')} />
            </Field>
            <Field label="Apply URL">
              <input className="input" type="url" value={form.apply_url} onChange={set('apply_url')} placeholder="https://…" />
            </Field>
            <Field label="Field / discipline">
              <select className="input" value={form.field_id} onChange={set('field_id')}>
                <option value="">Any field</option>
                {fields.map((f) => (
                  <option key={f.id} value={f.id}>
                    {f.name}
                  </option>
                ))}
              </select>
            </Field>
          </div>

          <Field label="Requirements">
            <textarea
              className="input min-h-[80px] resize-y"
              value={form.requirements}
              onChange={set('requirements')}
              placeholder="Key requirements, eligibility, etc."
            />
          </Field>

          <div className="grid sm:grid-cols-3 gap-4">
            <Field label="Min GPA (/4.0)">
              <input className="input" type="number" step="0.01" min="0" max="4" value={form.min_gpa} onChange={set('min_gpa')} />
            </Field>
            <Field label="Min score (/100)">
              <input className="input" type="number" min="0" max="100" value={form.min_score} onChange={set('min_score')} />
            </Field>
            <Field label="Graduation year">
              <input className="input" type="number" value={form.graduation_year} onChange={set('graduation_year')} />
            </Field>
          </div>

          <label className="flex items-center gap-2 text-sm text-cream/80">
            <input type="checkbox" checked={form.is_featured} onChange={set('is_featured')} className="accent-gold-400" />
            Feature this opportunity
          </label>

          <div className="flex justify-end gap-2 pt-2">
            <button type="button" onClick={onClose} className="btn-ghost text-sm">
              Cancel
            </button>
            <button type="submit" disabled={saving} className="btn-primary text-sm">
              {saving ? 'Saving…' : editing ? 'Save changes' : 'Post opportunity'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

function Field({ label, required, children }) {
  return (
    <label className="block">
      <span className="field-label">
        {label} {required && <span className="text-gold-400">*</span>}
      </span>
      {children}
    </label>
  );
}
