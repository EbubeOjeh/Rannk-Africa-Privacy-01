import { useEffect, useState } from 'react';
import { Calendar, Lock, Play, Plus } from 'lucide-react';
import toast from 'react-hot-toast';
import { cyclesService } from '@/services/cycles.service';
import { Loader } from '@/components/Loader';
import { PageGuide } from '@/components/PageGuide';
import { useAuth } from '@/hooks/useAuth';

const STATUSES = ['draft', 'open', 'review', 'published', 'closed'];

const NEXT_STATUS = {
  draft: ['open'],
  open: ['review', 'published'],
  review: ['published', 'open'],
  published: ['closed'],
  closed: [],
};

const PILLS = {
  draft: 'pill bg-cream/10 text-cream/70',
  open: 'pill-success',
  review: 'pill-pending',
  published: 'pill bg-amber-500/15 text-amber-200',
  closed: 'pill bg-rose-500/15 text-rose-300',
};

export default function Cycles() {
  const { role } = useAuth();
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);
  const [form, setForm] = useState({
    name: '',
    year: new Date().getFullYear(),
    submission_opens_at: '',
    submission_closes_at: '',
    review_ends_at: '',
    max_students_per_school: 15,
    description: '',
  });

  const refresh = () => {
    setLoading(true);
    cyclesService.list().then(setItems).finally(() => setLoading(false));
  };
  useEffect(refresh, []);

  const canManage = role === 'super_admin';

  const create = async (e) => {
    e.preventDefault();
    setCreating(true);
    try {
      const payload = { ...form };
      ['submission_opens_at', 'submission_closes_at', 'review_ends_at'].forEach((k) => {
        if (!payload[k]) delete payload[k];
      });
      await cyclesService.create(payload);
      toast.success('Cycle created.');
      setForm({
        name: '',
        year: new Date().getFullYear(),
        submission_opens_at: '',
        submission_closes_at: '',
        review_ends_at: '',
        max_students_per_school: 15,
        description: '',
      });
      refresh();
    } catch (err) {
      toast.error(err?.response?.data?.error?.message || 'Create failed.');
    } finally {
      setCreating(false);
    }
  };

  const transition = async (cycle, status) => {
    if (status === 'closed' && !confirm('Closing locks all scores in this cycle. Continue?')) return;
    try {
      await cyclesService.setStatus(cycle.id, status);
      toast.success(`Cycle now ${status}.`);
      refresh();
    } catch (err) {
      toast.error(err?.response?.data?.error?.message || 'Transition failed.');
    }
  };

  return (
    <div className="max-w-4xl">
      <PageGuide
        id="cycles"
        className="mb-6"
        title="How submission cycles control publishing"
        steps={[
          'Students are stamped with whichever cycle is OPEN when they register — if no cycle is open they get none and can never be published.',
          'Moving a cycle to PUBLISHED makes every approved student in it publicly visible, in bulk.',
          'CLOSED locks the cycle and freezes its scores permanently. Stop at PUBLISHED unless you mean to freeze.',
        ]}
      />
      <h1 className="font-display text-2xl font-bold">Submission Cycles</h1>
      <p className="text-sm text-cream/60 mt-1">
        Each cycle defines a 4–6 week submission window followed by 1–2 weeks of admin review.
        Schools may submit up to 15 students per cycle.
      </p>

      {canManage && (
        <form onSubmit={create} className="card p-6 mt-6 space-y-3">
          <h2 className="font-semibold flex items-center gap-2">
            <Plus className="w-4 h-4 text-gold-400" /> Create new cycle
          </h2>
          <div className="grid sm:grid-cols-2 gap-3">
            <Input label="Name" required value={form.name} onChange={(v) => setForm({ ...form, name: v })} />
            <Input label="Year" type="number" required value={form.year} onChange={(v) => setForm({ ...form, year: Number(v) })} />
            <Input label="Submissions open" type="datetime-local" value={form.submission_opens_at} onChange={(v) => setForm({ ...form, submission_opens_at: v })} />
            <Input label="Submissions close" type="datetime-local" value={form.submission_closes_at} onChange={(v) => setForm({ ...form, submission_closes_at: v })} />
            <Input label="Review ends" type="datetime-local" value={form.review_ends_at} onChange={(v) => setForm({ ...form, review_ends_at: v })} />
            <Input label="Max students per school" type="number" value={form.max_students_per_school} onChange={(v) => setForm({ ...form, max_students_per_school: Number(v) })} />
          </div>
          <Input label="Description" value={form.description} onChange={(v) => setForm({ ...form, description: v })} />
          <div className="flex justify-end">
            <button type="submit" disabled={creating} className="btn-primary">
              <Plus className="w-4 h-4" /> Create cycle
            </button>
          </div>
        </form>
      )}

      <div className="card mt-6 divide-y divide-cream/10">
        {loading ? (
          <Loader />
        ) : items.length === 0 ? (
          <div className="p-6 text-sm text-cream/60">No cycles yet.</div>
        ) : (
          items.map((c) => (
            <div key={c.id} className="p-5 grid sm:grid-cols-12 gap-3 items-center">
              <div className="sm:col-span-5">
                <div className="flex items-center gap-2">
                  <Calendar className="w-4 h-4 text-gold-400" />
                  <span className="font-semibold">{c.name}</span>
                  <span className="text-cream/40 text-xs">{c.year}</span>
                  {c.is_locked && <Lock className="w-3.5 h-3.5 text-rose-300" />}
                </div>
                {c.description && <p className="text-xs text-cream/60 mt-1">{c.description}</p>}
                <p className="text-[11px] text-cream/40 mt-1">
                  Max {c.max_students_per_school} per school
                </p>
              </div>
              <div className="sm:col-span-3 text-xs text-cream/60">
                {c.submission_opens_at ? new Date(c.submission_opens_at).toLocaleDateString() : '—'} →{' '}
                {c.submission_closes_at ? new Date(c.submission_closes_at).toLocaleDateString() : '—'}
              </div>
              <div className="sm:col-span-2">
                <span className={PILLS[c.status]}>{c.status}</span>
              </div>
              <div className="sm:col-span-2 flex justify-end gap-1 flex-wrap">
                {canManage &&
                  NEXT_STATUS[c.status].map((s) => (
                    <button
                      key={s}
                      onClick={() => transition(c, s)}
                      className="btn-ghost text-xs"
                      title={`Move to ${s}`}
                    >
                      <Play className="w-3 h-3" /> {s}
                    </button>
                  ))}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}

function Input({ label, value, onChange, type = 'text', required }) {
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
