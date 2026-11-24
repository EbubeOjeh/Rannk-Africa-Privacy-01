import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Briefcase, ShieldCheck } from 'lucide-react';
import toast from 'react-hot-toast';
import { AuthShell, AuthHeader } from '@/components/AuthShell';
import { TermsAgreement } from '@/components/TermsAgreement';
import { recruitersService } from '@/services/recruiters.service';
import { useAuth } from '@/hooks/useAuth';

const empty = { name: '', organization: '', email: '', password: '' };

export default function RecruiterRegister() {
  const [form, setForm] = useState(empty);
  const [submitting, setSubmitting] = useState(false);
  const [accepted, setAccepted] = useState(false);
  const { setSession } = useAuth();
  const navigate = useNavigate();

  const submit = async (e) => {
    e.preventDefault();
    if (!accepted) {
      toast.error('Please agree to the Terms & Conditions to continue.');
      return;
    }
    setSubmitting(true);
    try {
      const res = await recruitersService.register({ ...form, accept_terms: true });
      setSession({ user: res.user, tokens: res.tokens });
      toast.success('Account created — pending approval. You can browse rankings now.', { duration: 6000 });
      navigate('/rankings', { replace: true });
    } catch (err) {
      toast.error(err?.response?.data?.error?.message || 'Registration failed.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <AuthShell>
      <AuthHeader
        icon={Briefcase}
        title="Recruiter / Organization access"
        subtitle="Register to discover top-ranked students. Contact details unlock once RankAfrica verifies your account."
      />
      <motion.form
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        onSubmit={submit}
      >
        <div className="card p-6 space-y-4">
            <div className="rounded-lg bg-gold-400/[0.06] border border-gold-400/15 px-4 py-3 text-xs text-cream/80 flex gap-2">
              <ShieldCheck className="w-4 h-4 text-gold-400 shrink-0 mt-0.5" />
              <div>Your request enters an approval queue. An admin verifies recruiters before contact information is shared.</div>
            </div>
            <div>
              <label className="field-label">Your name</label>
              <input className="input" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} placeholder="Full name" required />
            </div>
            <div>
              <label className="field-label">Organization</label>
              <input className="input" value={form.organization} onChange={(e) => setForm({ ...form, organization: e.target.value })} placeholder="Company / organization" required />
            </div>
            <div>
              <label className="field-label">Email</label>
              <input type="email" className="input" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} placeholder="you@company.com" required />
            </div>
            <div>
              <label className="field-label">Password</label>
              <input type="password" className="input" minLength={8} value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} placeholder="At least 8 characters" required />
            </div>
            <TermsAgreement accepted={accepted} onChange={setAccepted} />
            <button type="submit" disabled={submitting || !accepted} className="btn-primary w-full">
              {submitting ? 'Submitting…' : 'Request recruiter access'}
            </button>
            <p className="text-center text-xs text-cream/60">
              Already have an account?{' '}
              <Link to="/login" className="text-gold-300 hover:underline">Sign in</Link>
            </p>
        </div>
      </motion.form>
    </AuthShell>
  );
}
