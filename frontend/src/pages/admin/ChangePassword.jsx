import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { KeyRound, ShieldCheck } from 'lucide-react';
import toast from 'react-hot-toast';
import { authService } from '@/services/auth.service';
import { useAuth } from '@/hooks/useAuth';

export default function ChangePassword() {
  const { user, mustChangePassword, setUser } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({ current: '', next: '', confirm: '' });
  const [busy, setBusy] = useState(false);

  const submit = async (e) => {
    e.preventDefault();
    if (form.next.length < 8) return toast.error('New password must be at least 8 characters.');
    if (form.next !== form.confirm) return toast.error('New passwords do not match.');
    setBusy(true);
    try {
      await authService.changePassword(form.current, form.next);
      const me = await authService.me();
      setUser(me);
      toast.success('Password updated.');
      navigate('/admin', { replace: true });
    } catch (err) {
      toast.error(err?.response?.data?.error?.message || 'Could not change password.');
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="max-w-md mx-auto">
      <div className="text-center mb-5">
        <ShieldCheck className="w-7 h-7 text-gold-400 mx-auto" />
        <h1 className="font-display text-2xl font-bold mt-2">
          {mustChangePassword ? 'Set your password' : 'Change password'}
        </h1>
        <p className="text-sm text-cream/60 mt-1">
          {mustChangePassword
            ? `Welcome${user?.name ? `, ${user.name}` : ''}! For security, choose a new password before continuing.`
            : 'Update the password you use to sign in.'}
        </p>
      </div>

      <form onSubmit={submit} className="card p-6 space-y-4">
        <div>
          <label className="field-label">Current password</label>
          <input
            type="password"
            className="input"
            value={form.current}
            onChange={(e) => setForm({ ...form, current: e.target.value })}
            placeholder={mustChangePassword ? 'rankpass' : 'Current password'}
            required
          />
        </div>
        <div>
          <label className="field-label">New password</label>
          <input
            type="password"
            className="input"
            value={form.next}
            onChange={(e) => setForm({ ...form, next: e.target.value })}
            placeholder="At least 8 characters"
            minLength={8}
            required
          />
        </div>
        <div>
          <label className="field-label">Confirm new password</label>
          <input
            type="password"
            className="input"
            value={form.confirm}
            onChange={(e) => setForm({ ...form, confirm: e.target.value })}
            placeholder="Re-enter new password"
            minLength={8}
            required
          />
        </div>
        <button type="submit" disabled={busy} className="btn-primary w-full">
          <KeyRound className="w-4 h-4" />
          {busy ? 'Saving…' : 'Update password'}
        </button>
      </form>
    </div>
  );
}
