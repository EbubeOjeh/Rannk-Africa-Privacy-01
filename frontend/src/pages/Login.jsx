import { useState } from 'react';
import { Link, useLocation, useNavigate, useSearchParams } from 'react-router-dom';
import { Eye, EyeOff, LogIn, ChevronRight, ArrowLeft } from 'lucide-react';
import { motion } from 'framer-motion';
import toast from 'react-hot-toast';
import { authService } from '@/services/auth.service';
import { useAuth } from '@/hooks/useAuth';
import { AuthShell, AuthHeader } from '@/components/AuthShell';
import { ACCOUNT_TYPES, ACCOUNT_TYPE_LIST } from '@/utils/accountTypes';

export default function Login() {
  const [params, setParams] = useSearchParams();
  const selected = ACCOUNT_TYPES[params.get('as')] || null;

  // No audience chosen yet → show the chooser so the user can tell us who
  // they are; the form then addresses them directly.
  if (!selected) {
    return (
      <AuthShell maxWidth="max-w-lg">
        <div className="text-center mb-7">
          <h1 className="font-display text-2xl font-bold">Sign in to RankAfrica</h1>
          <p className="text-sm text-cream/60 mt-1">Choose the account you're signing in with.</p>
        </div>
        <div className="grid sm:grid-cols-2 gap-3">
          {ACCOUNT_TYPE_LIST.map((t) => (
            <button
              key={t.key}
              onClick={() => setParams({ as: t.key })}
              className="card p-5 text-left flex items-center gap-4 hover:border-gold-400/40 transition-colors group"
            >
              <span className="w-11 h-11 shrink-0 rounded-xl bg-gold-400/15 grid place-content-center text-gold-400 group-hover:bg-gold-400/25 transition-colors">
                <t.icon className="w-5 h-5" />
              </span>
              <span className="min-w-0 flex-1">
                <span className="block font-semibold text-white">{t.label}</span>
                <span className="block text-xs text-cream/55 truncate">{t.blurb}</span>
              </span>
              <ChevronRight className="w-4 h-4 text-cream/40 group-hover:text-gold-300 transition-colors" />
            </button>
          ))}
        </div>
      </AuthShell>
    );
  }

  return <LoginForm type={selected} onBack={() => setParams({})} />;
}

function LoginForm({ type, onBack }) {
  const [form, setForm] = useState({ email: '', password: '' });
  const [showPwd, setShowPwd] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const { setSession } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const next = location.state?.from?.pathname || '/admin';

  const handle = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      const data = await authService.login(form.email, form.password);
      setSession({ user: data.user, tokens: data.tokens });
      toast.success('Welcome back!');
      // Route by the role the backend returns (not the chosen tab): students go
      // to their dashboard, employers to theirs, staff/schools to the admin app.
      const role = data.user?.role;
      const dest = data.user?.must_change_password
        ? '/admin/change-password'
        : role === 'student'
        ? '/student/study'
        : ['school_admin','university_admin'].includes(role)
        ? '/school'
        : role === 'employer'
        ? '/employer'
        : next;
      navigate(dest, { replace: true });
    } catch (err) {
      toast.error(err?.response?.data?.error?.message || 'Authentication failed.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <AuthShell>
      <button
        onClick={onBack}
        className="inline-flex items-center gap-1.5 text-xs text-cream/50 hover:text-cream/80 mb-4 transition-colors"
      >
        <ArrowLeft className="w-3.5 h-3.5" /> Choose a different account type
      </button>

      <AuthHeader icon={type.icon} title={type.title} subtitle={type.blurb} />

      <motion.form
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        onSubmit={handle}
        className="card p-6 space-y-4"
      >
        <div>
          <label className="field-label">Email</label>
          <input
            type="email"
            className="input"
            value={form.email}
            onChange={(e) => setForm({ ...form, email: e.target.value })}
            placeholder="you@example.com"
            required
            autoFocus
          />
        </div>
        <div>
          <label className="field-label">Password</label>
          <div className="relative">
            <input
              type={showPwd ? 'text' : 'password'}
              className="input pr-10"
              value={form.password}
              onChange={(e) => setForm({ ...form, password: e.target.value })}
              placeholder="Enter password"
              required
              minLength={6}
            />
            <button
              type="button"
              className="absolute right-2 top-1/2 -translate-y-1/2 text-white/40 hover:text-white"
              onClick={() => setShowPwd((v) => !v)}
              aria-label="Toggle password visibility"
            >
              {showPwd ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
            </button>
          </div>
        </div>

        <button type="submit" disabled={submitting} className="btn-primary w-full">
          <LogIn className="w-4 h-4" />
          {submitting ? 'Please wait…' : 'Sign In'}
        </button>

        {type.register && (
          <p className="text-center text-xs text-cream/60">
            New here?{' '}
            <Link to={type.register.to} className="text-gold-300 hover:underline">
              {type.register.label}
            </Link>
          </p>
        )}
        {type.key === 'employee' && (
          <p className="text-center text-xs text-cream/50">
            Employee accounts are created by a RankAfrica administrator.
          </p>
        )}
      </motion.form>
    </AuthShell>
  );
}
