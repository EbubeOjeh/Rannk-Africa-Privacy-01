import { useEffect, useState } from 'react';
import { FlaskConical, Plus, Trash2, Lock, Unlock, X, Clock } from 'lucide-react';
import toast from 'react-hot-toast';
import { testAccountsService } from '@/services/testAccounts.service';
import { universitiesService } from '@/services/universities.service';
import { Loader } from '@/components/Loader';
import { EmptyState } from '@/components/EmptyState';
import { PageGuide } from '@/components/PageGuide';

const TYPES = [
  ['student', 'Student'],
  ['recruiter', 'Recruiter / Organization'],
];
const typeLabel = (t) => TYPES.find(([v]) => v === t)?.[1] || t;

const emptyForm = {
  account_type: 'student',
  name: '',
  email: '',
  password: '',
  university_id: '',
  organization: '',
  course: '',
};

export default function TestAccounts() {
  const [items, setItems] = useState([]);
  const [universities, setUniversities] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState(emptyForm);
  const [creating, setCreating] = useState(false);
  const [busy, setBusy] = useState(null);

  const setField = (k, v) => setForm((f) => ({ ...f, [k]: v }));

  const load = () => {
    setLoading(true);
    testAccountsService
      .list()
      .then((d) => setItems(Array.isArray(d) ? d : []))
      .catch(() => setItems([]))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    load();
    universitiesService
      .list({ page_size: 100 })
      .then((d) => setUniversities(d.items || []))
      .catch(() => setUniversities([]));
  }, []);

  const needsUniversity = form.account_type === 'student';

  const create = async (e) => {
    e.preventDefault();
    setCreating(true);
    try {
      const payload = {
        account_type: form.account_type,
        name: form.name,
        email: form.email,
        password: form.password,
      };
      if (needsUniversity && form.university_id) payload.university_id = form.university_id;
      if (form.account_type === 'recruiter' && form.organization) payload.organization = form.organization;
      if (form.account_type === 'student' && form.course) payload.course = form.course;
      await testAccountsService.create(payload);
      toast.success('Test account created.');
      setForm(emptyForm);
      setShowForm(false);
      load();
    } catch (err) {
      toast.error(err?.response?.data?.error?.message || 'Could not create account.');
    } finally {
      setCreating(false);
    }
  };

  const toggleBlock = async (a) => {
    setBusy(a.id);
    try {
      await (a.is_active ? testAccountsService.block(a.id) : testAccountsService.unblock(a.id));
      toast.success(a.is_active ? 'Account blocked.' : 'Account unblocked.');
      load();
    } catch (err) {
      toast.error(err?.response?.data?.error?.message || 'Action failed.');
    } finally {
      setBusy(null);
    }
  };

  const remove = async (a) => {
    if (!confirm(`Delete the test account “${a.email}”? This cannot be undone.`)) return;
    setBusy(a.id);
    try {
      await testAccountsService.remove(a.id);
      toast.success('Test account deleted.');
      setItems((prev) => prev.filter((x) => x.id !== a.id));
    } catch (err) {
      toast.error(err?.response?.data?.error?.message || 'Delete failed.');
    } finally {
      setBusy(null);
    }
  };

  return (
    <div>
      <PageGuide
        id="test-accounts"
        className="mb-6"
        title="Test accounts"
        steps={[
          'Accounts created here are flagged as test data and auto-delete after 20 days.',
          'Use them to walk through the student or recruiter experience without polluting the real leaderboard.',
          'Delete them before launch — only test-flagged accounts can be removed from this page.',
        ]}
      />
      <div className="flex items-start justify-between gap-4">
        <div>
          <h1 className="font-display text-2xl font-bold flex items-center gap-2">
            <FlaskConical className="w-6 h-6 text-gold-400" /> Test Accounts
          </h1>
          <p className="text-sm text-cream/60 mt-1 max-w-2xl">
            Create dummy logins to test the student and recruiter flows. Each account is
            <span className="text-cream/80"> automatically deleted 20 days after creation</span>; you
            can also block or delete one here at any time.
          </p>
        </div>
        <button onClick={() => setShowForm((s) => !s)} className="btn-primary shrink-0">
          {showForm ? <X className="w-4 h-4" /> : <Plus className="w-4 h-4" />}
          {showForm ? 'Cancel' : 'Create test account'}
        </button>
      </div>

      {showForm && (
        <form onSubmit={create} className="card p-6 mt-6 space-y-3">
          <h2 className="font-semibold flex items-center gap-2">
            <Plus className="w-4 h-4 text-gold-400" /> New test account
          </h2>
          <div className="grid sm:grid-cols-2 gap-3">
            <label className="block">
              <span className="field-label">Account type</span>
              <select
                className="input"
                value={form.account_type}
                onChange={(e) => setField('account_type', e.target.value)}
              >
                {TYPES.map(([v, label]) => (
                  <option key={v} value={v}>
                    {label}
                  </option>
                ))}
              </select>
            </label>
            <Field label="Full name" required value={form.name} onChange={(v) => setField('name', v)} />
            <Field label="Email" type="email" required value={form.email} onChange={(v) => setField('email', v)} />
            <Field
              label="Password"
              type="text"
              required
              value={form.password}
              onChange={(v) => setField('password', v)}
              placeholder="At least 6 characters (share with your tester)"
            />
            {needsUniversity && (
              <label className="block">
                <span className="field-label">University</span>
                <select
                  className="input"
                  value={form.university_id}
                  onChange={(e) => setField('university_id', e.target.value)}
                >
                  <option value="">
                    {form.account_type === 'student' ? 'Default (first university)' : 'Select a university…'}
                  </option>
                  {universities.map((u) => (
                    <option key={u.id} value={u.id}>
                      {u.name}
                    </option>
                  ))}
                </select>
              </label>
            )}
            {form.account_type === 'recruiter' && (
              <Field
                label="Organization"
                value={form.organization}
                onChange={(v) => setField('organization', v)}
                placeholder="Defaults to the account name"
              />
            )}
            {form.account_type === 'student' && (
              <Field
                label="Course (optional)"
                value={form.course}
                onChange={(v) => setField('course', v)}
                placeholder="e.g. Computer Science"
              />
            )}
          </div>
          <div className="flex justify-end">
            <button
              type="submit"
              disabled={creating || !form.name.trim() || !form.email.trim() || form.password.length < 6}
              className="btn-primary"
            >
              <Plus className="w-4 h-4" /> {creating ? 'Creating…' : 'Create account'}
            </button>
          </div>
        </form>
      )}

      <div className="card mt-6 overflow-x-auto">
        <div className="data-head">
          <div className="col-span-3">Email</div>
          <div className="col-span-2">Type</div>
          <div className="col-span-2">Status</div>
          <div className="col-span-3">Auto-deletes</div>
          <div className="col-span-2 text-right">Actions</div>
        </div>
        {loading ? (
          <Loader />
        ) : items.length === 0 ? (
          <EmptyState
            icon={FlaskConical}
            title="No test accounts yet"
            description="Create a dummy student or recruiter login to test the flows."
          />
        ) : (
          items.map((a) => (
            <div key={a.id} className="data-row">
              <div className="col-span-3 min-w-0">
                <div className="font-medium truncate">{a.email}</div>
                <div className="text-[11px] text-cream/40 truncate">{a.name}</div>
              </div>
              <div className="col-span-2 text-sm text-cream/70 truncate">{typeLabel(a.account_type)}</div>
              <div className="col-span-2">
                <span className={a.is_active ? 'pill-success' : 'pill bg-cream/10 text-cream/60'}>
                  {a.is_active ? 'Active' : 'Blocked'}
                </span>
              </div>
              <div className="col-span-3 text-xs text-cream/60 inline-flex items-center gap-1.5">
                <Clock className="w-3.5 h-3.5" />
                {a.days_left > 0 ? `in ${a.days_left} day${a.days_left === 1 ? '' : 's'}` : 'today'}
              </div>
              <div className="col-span-2 flex justify-end gap-1">
                <button
                  disabled={busy === a.id}
                  onClick={() => toggleBlock(a)}
                  className="btn-ghost h-8 px-2 text-xs text-amber-200"
                  title={a.is_active ? 'Block' : 'Unblock'}
                >
                  {a.is_active ? <Lock className="w-3.5 h-3.5" /> : <Unlock className="w-3.5 h-3.5" />}
                  {a.is_active ? 'Block' : 'Unblock'}
                </button>
                <button
                  disabled={busy === a.id}
                  onClick={() => remove(a)}
                  className="btn-ghost h-8 w-8 p-0 text-rose-300"
                  title="Delete"
                >
                  <Trash2 className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}

function Field({ label, value, onChange, type = 'text', required, placeholder }) {
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
        placeholder={placeholder}
      />
    </label>
  );
}
