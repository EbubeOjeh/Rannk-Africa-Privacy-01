import { useEffect, useState } from 'react';
import { Building2, BadgeCheck, Star, Save } from 'lucide-react';
import toast from 'react-hot-toast';
import { Loader } from '@/components/Loader';
import { employerService } from '@/services/employer.service';

const EMPTY = {
  company_name: '',
  logo_url: '',
  website: '',
  about: '',
  industry: '',
  location: '',
  company_size: '',
};

const SIZES = ['', '1-10', '11-50', '51-200', '201-500', '501-1000', '1000+'];

export default function EmployerProfile() {
  const [form, setForm] = useState(EMPTY);
  const [meta, setMeta] = useState({ is_verified: false, is_featured: false });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    employerService
      .getProfile()
      .then((p) => {
        if (!p) return;
        setForm({
          company_name: p.company_name || '',
          logo_url: p.logo_url || '',
          website: p.website || '',
          about: p.about || '',
          industry: p.industry || '',
          location: p.location || '',
          company_size: p.company_size || '',
        });
        setMeta({ is_verified: Boolean(p.is_verified), is_featured: Boolean(p.is_featured) });
      })
      // 404 = no profile yet; start from a blank form.
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const set = (k) => (e) => setForm((f) => ({ ...f, [k]: e.target.value }));

  const submit = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      // Only send keys with a value (besides the required company_name).
      const payload = { company_name: form.company_name };
      ['logo_url', 'website', 'about', 'industry', 'location', 'company_size'].forEach((k) => {
        if (form[k] !== '') payload[k] = form[k];
      });
      const saved = await employerService.saveProfile(payload);
      if (saved) {
        setMeta({ is_verified: Boolean(saved.is_verified), is_featured: Boolean(saved.is_featured) });
      }
      toast.success('Company profile saved.');
    } catch (err) {
      toast.error(err?.response?.data?.error?.message || 'Could not save profile.');
    } finally {
      setSaving(false);
    }
  };

  if (loading) return <Loader label="Loading company profile…" />;

  return (
    <div className="max-w-2xl">
      <div className="flex items-center justify-between gap-3 flex-wrap">
        <div>
          <h1 className="font-display text-2xl font-bold flex items-center gap-2">
            <Building2 className="w-5 h-5 text-gold-400" /> Company profile
          </h1>
          <p className="text-sm text-cream/60 mt-1">
            How your organisation appears to students across RankAfrica.
          </p>
        </div>
        <div className="flex items-center gap-2">
          {meta.is_verified && (
            <span className="pill-success">
              <BadgeCheck className="w-3.5 h-3.5" /> Verified
            </span>
          )}
          {meta.is_featured && (
            <span className="pill bg-gold-400/15 text-gold-300">
              <Star className="w-3.5 h-3.5" /> Featured
            </span>
          )}
        </div>
      </div>

      <form onSubmit={submit} className="card p-6 mt-6 space-y-4">
        <Field label="Company name" required>
          <input className="input" value={form.company_name} onChange={set('company_name')} required />
        </Field>
        <div className="grid sm:grid-cols-2 gap-4">
          <Field label="Industry">
            <input className="input" value={form.industry} onChange={set('industry')} placeholder="e.g. Fintech" />
          </Field>
          <Field label="Location">
            <input className="input" value={form.location} onChange={set('location')} placeholder="e.g. Lagos, Nigeria" />
          </Field>
          <Field label="Website">
            <input className="input" type="url" value={form.website} onChange={set('website')} placeholder="https://…" />
          </Field>
          <Field label="Company size">
            <select className="input" value={form.company_size} onChange={set('company_size')}>
              {SIZES.map((s) => (
                <option key={s} value={s}>
                  {s === '' ? 'Select size…' : `${s} employees`}
                </option>
              ))}
            </select>
          </Field>
        </div>
        <Field label="Logo URL">
          <input className="input" type="url" value={form.logo_url} onChange={set('logo_url')} placeholder="https://…/logo.png" />
        </Field>
        {form.logo_url && (
          <img
            src={form.logo_url}
            alt="Logo preview"
            className="h-12 w-12 rounded-lg object-contain bg-white/5 p-1"
            onError={(e) => (e.currentTarget.style.display = 'none')}
          />
        )}
        <Field label="About">
          <textarea
            className="input min-h-[120px] resize-y"
            value={form.about}
            onChange={set('about')}
            placeholder="Tell students about your company, mission, and what you look for."
          />
        </Field>

        <div className="flex justify-end">
          <button type="submit" disabled={saving} className="btn-primary">
            <Save className="w-4 h-4" /> {saving ? 'Saving…' : 'Save profile'}
          </button>
        </div>
      </form>
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
