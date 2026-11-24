import { useEffect, useState } from 'react';
import { RotateCcw, ShieldBan, UserX } from 'lucide-react';
import toast from 'react-hot-toast';
import { adminService } from '@/services/admin.service';
import { Loader } from '@/components/Loader';
import { EmptyState } from '@/components/EmptyState';

export default function Moderation() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(null);
  const [form, setForm] = useState({ user_id: '', reason: '' });
  const [suspending, setSuspending] = useState(false);

  const load = () => {
    setLoading(true);
    adminService
      .suspendedUsers()
      .then((d) => setItems(Array.isArray(d) ? d : []))
      .catch(() => setItems([]))
      .finally(() => setLoading(false));
  };
  useEffect(load, []);

  const suspend = async (e) => {
    e.preventDefault();
    const id = form.user_id.trim();
    if (!id) return;
    setSuspending(true);
    try {
      await adminService.suspendUser(id, form.reason.trim() || null);
      toast.success('User suspended.');
      setForm({ user_id: '', reason: '' });
      load();
    } catch (err) {
      toast.error(err?.response?.data?.error?.message || 'Suspend failed.');
    } finally {
      setSuspending(false);
    }
  };

  const unsuspend = async (u) => {
    setBusy(u.id);
    try {
      await adminService.unsuspendUser(u.id);
      toast.success('User reinstated.');
      setItems((prev) => prev.filter((x) => x.id !== u.id));
    } catch (err) {
      toast.error(err?.response?.data?.error?.message || 'Action failed.');
    } finally {
      setBusy(null);
    }
  };

  return (
    <div>
      <h1 className="font-display text-2xl font-bold flex items-center gap-2">
        <ShieldBan className="w-6 h-6 text-gold-400" /> Moderation
      </h1>
      <p className="text-sm text-cream/60 mt-1">
        Suspend platform users who breach the rules, and reinstate them when resolved.
      </p>

      {/* Suspend a user */}
      <form onSubmit={suspend} className="card p-6 mt-6 space-y-3">
        <h2 className="font-semibold flex items-center gap-2">
          <UserX className="w-4 h-4 text-gold-400" /> Suspend a user
        </h2>
        <div className="grid sm:grid-cols-2 gap-3">
          <label className="block">
            <span className="field-label">User ID <span className="text-gold-400">*</span></span>
            <input
              className="input"
              placeholder="User ID"
              value={form.user_id}
              onChange={(e) => setForm({ ...form, user_id: e.target.value })}
              required
            />
          </label>
          <label className="block">
            <span className="field-label">Reason (optional)</span>
            <input
              className="input"
              placeholder="Reason shown to the user"
              value={form.reason}
              onChange={(e) => setForm({ ...form, reason: e.target.value })}
            />
          </label>
        </div>
        <div className="flex justify-end">
          <button type="submit" disabled={suspending || !form.user_id.trim()} className="btn-primary">
            <UserX className="w-4 h-4" /> {suspending ? 'Suspending…' : 'Suspend user'}
          </button>
        </div>
      </form>

      {/* Suspended users */}
      <h2 className="mt-8 font-semibold">Suspended users</h2>
      <div className="card mt-3 overflow-x-auto">
        <div className="data-head">
          <div className="col-span-4">User</div>
          <div className="col-span-2">Role</div>
          <div className="col-span-4">Reason</div>
          <div className="col-span-2 text-right">Action</div>
        </div>
        {loading ? (
          <Loader />
        ) : items.length === 0 ? (
          <EmptyState
            icon={ShieldBan}
            title="No suspended users"
            description="Suspended accounts will appear here for review."
          />
        ) : (
          items.map((u) => (
            <div key={u.id} className="data-row">
              <div className="col-span-4 min-w-0">
                <div className="font-medium truncate">{u.name || '—'}</div>
                <div className="text-[11px] text-cream/50 truncate">{u.email || ''}</div>
              </div>
              <div className="col-span-2 text-sm text-cream/70 truncate capitalize">
                {String(u.role || '—').replace(/_/g, ' ')}
              </div>
              <div className="col-span-4 text-sm text-cream/70 truncate" title={u.suspension_reason || ''}>
                {u.suspension_reason || '—'}
                {u.suspended_at && (
                  <span className="block text-[11px] text-cream/40">
                    {new Date(u.suspended_at).toLocaleDateString()}
                  </span>
                )}
              </div>
              <div className="col-span-2 flex justify-end">
                <button
                  disabled={busy === u.id}
                  onClick={() => unsuspend(u)}
                  className="btn-ghost h-8 px-2 text-xs text-emerald-300"
                  title="Unsuspend"
                >
                  <RotateCcw className="w-3.5 h-3.5" /> Unsuspend
                </button>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
