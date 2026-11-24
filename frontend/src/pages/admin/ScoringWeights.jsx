import { useEffect, useMemo, useState } from 'react';
import { RotateCcw, Save, SlidersHorizontal } from 'lucide-react';
import toast from 'react-hot-toast';
import { adminService } from '@/services/admin.service';
import { Loader } from '@/components/Loader';
import { PageGuide } from '@/components/PageGuide';

// The six categories whose weights combine into the final /100 score.
const FIELDS = [
  { key: 'academic', label: 'Academic', hint: 'WES-style GPA equivalency' },
  { key: 'research', label: 'Research', hint: 'Verified publications & research' },
  { key: 'project', label: 'Project', hint: 'AI rubric-scored projects' },
  { key: 'leadership', label: 'Leadership', hint: 'Verified leadership roles' },
  { key: 'experience', label: 'Experience', hint: 'Internships & work experience' },
  { key: 'competition', label: 'Competition', hint: 'Hackathons & contests' },
];

const toNum = (v) => (v === '' || v === null || v === undefined ? 0 : Number(v) || 0);

export default function ScoringWeights() {
  const [weights, setWeights] = useState(null);
  const [defaults, setDefaults] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    adminService
      .getWeights()
      .then((d) => {
        setWeights({ ...(d?.weights || {}) });
        setDefaults({ ...(d?.defaults || {}) });
      })
      .catch(() => toast.error('Could not load scoring weights.'))
      .finally(() => setLoading(false));
  }, []);

  const sum = useMemo(
    () => FIELDS.reduce((t, f) => t + toNum(weights?.[f.key]), 0),
    [weights]
  );

  const setField = (key, value) =>
    setWeights((w) => ({ ...w, [key]: value === '' ? '' : Number(value) }));

  const resetToDefaults = () => {
    if (!defaults) return;
    setWeights({ ...defaults });
    toast('Reset to defaults — remember to save.', { icon: '↩️' });
  };

  const save = async () => {
    setSaving(true);
    try {
      const payload = {};
      FIELDS.forEach((f) => {
        payload[f.key] = toNum(weights?.[f.key]);
      });
      const updated = await adminService.saveWeights(payload);
      if (updated?.weights) setWeights({ ...updated.weights });
      toast.success('Weights saved — rankings recomputed.');
    } catch (err) {
      toast.error(err?.response?.data?.error?.message || 'Save failed.');
    } finally {
      setSaving(false);
    }
  };

  if (loading) return <Loader />;

  // A balanced 100-point split is the natural target, but the API accepts any
  // numbers (it normalizes server-side), so we only surface this as guidance.
  const near100 = Math.abs(sum - 100) < 0.001;

  return (
    <div className="max-w-3xl">
      <PageGuide
        id="scoring-weights"
        className="mb-6"
        title="Changing how students are scored"
        steps={[
          'These weights decide how the /100 index is split across academics, projects and achievements.',
          'Saving recomputes every ranking on the platform immediately.',
          'The public “How it works” section on the home page describes the default split — update it if you change these materially.',
        ]}
      />
      <h1 className="font-display text-2xl font-bold flex items-center gap-2">
        <SlidersHorizontal className="w-6 h-6 text-gold-400" /> Scoring Weights
      </h1>
      <p className="text-sm text-cream/60 mt-1">
        These six weights determine how each category contributes to a student&apos;s final
        <span className="text-gold-300"> /100</span> score. Saving recomputes every ranking on the platform.
      </p>

      <div className="card p-6 mt-6 space-y-4">
        <div className="grid sm:grid-cols-2 gap-4">
          {FIELDS.map((f) => (
            <label key={f.key} className="block">
              <span className="field-label">{f.label}</span>
              <input
                type="number"
                step="0.5"
                min="0"
                className="input"
                value={weights?.[f.key] ?? ''}
                onChange={(e) => setField(f.key, e.target.value)}
              />
              <span className="text-[11px] text-cream/40 mt-1 block">{f.hint}</span>
            </label>
          ))}
        </div>

        {/* Live sum indicator */}
        <div className="flex items-center justify-between rounded-lg bg-ink-900 border border-cream/10 px-4 py-3">
          <span className="text-sm text-cream/70">Total weight</span>
          <span
            className={`font-display text-xl font-bold tabular-nums ${
              near100 ? 'text-emerald-300' : 'text-gold-400'
            }`}
          >
            {sum.toFixed(1)}
            <span className="text-cream/40 text-sm font-normal"> / 100</span>
          </span>
        </div>
        {!near100 && (
          <p className="text-[11px] text-amber-200/80">
            Weights don&apos;t add up to 100. That&apos;s allowed — they&apos;ll be normalized — but a 100-point split is easiest to reason about.
          </p>
        )}

        <div className="flex items-center justify-end gap-2 pt-1">
          <button onClick={resetToDefaults} disabled={!defaults} className="btn-ghost" type="button">
            <RotateCcw className="w-4 h-4" /> Reset to defaults
          </button>
          <button onClick={save} disabled={saving} className="btn-primary" type="button">
            <Save className="w-4 h-4" /> {saving ? 'Saving…' : 'Save weights'}
          </button>
        </div>
      </div>
    </div>
  );
}
