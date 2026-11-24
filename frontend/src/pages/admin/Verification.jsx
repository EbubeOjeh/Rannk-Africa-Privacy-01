import { useEffect, useState } from 'react';
import { BadgeCheck, Check, FlaskConical, Briefcase, Trophy, Users, X } from 'lucide-react';
import toast from 'react-hot-toast';
import { adminService } from '@/services/admin.service';
import { Loader } from '@/components/Loader';
import { EmptyState } from '@/components/EmptyState';
import { PageGuide } from '@/components/PageGuide';

// Each pending bucket maps to a `kind` segment in POST /verification/{kind}/{id}.
const SECTIONS = [
  { key: 'research', kind: 'research', label: 'Research', icon: FlaskConical },
  { key: 'experience', kind: 'experience', label: 'Experience', icon: Briefcase },
  { key: 'competitions', kind: 'competition', label: 'Competitions', icon: Trophy },
  { key: 'leadership', kind: 'leadership', label: 'Leadership', icon: Users },
];

export default function Verification() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(null);
  const [active, setActive] = useState('research');

  const load = () => {
    setLoading(true);
    adminService
      .pendingVerifications()
      .then((d) => setData(d || {}))
      .catch(() => setData({}))
      .finally(() => setLoading(false));
  };
  useEffect(load, []);

  const count = (key) => {
    if (data?.counts && data.counts[key] != null) return data.counts[key];
    return Array.isArray(data?.[key]) ? data[key].length : 0;
  };

  const decide = async (section, item, decision) => {
    let rejection_reason = null;
    if (decision === 'rejected') {
      rejection_reason = prompt('Reason for rejection (shown to the student):');
      if (rejection_reason === null) return;
    }
    setBusy(`${section.key}:${item.id}`);
    try {
      await adminService.verifyItem(section.kind, item.id, {
        verification_status: decision,
        rejection_reason,
      });
      toast.success(decision === 'verified' ? 'Item verified.' : 'Item rejected.');
      // Optimistically drop the resolved item from its bucket.
      setData((prev) => ({
        ...prev,
        [section.key]: (prev?.[section.key] || []).filter((i) => i.id !== item.id),
      }));
    } catch (err) {
      toast.error(err?.response?.data?.error?.message || 'Action failed.');
    } finally {
      setBusy(null);
    }
  };

  if (loading) return <Loader />;

  const current = SECTIONS.find((s) => s.key === active);
  const items = Array.isArray(data?.[active]) ? data[active] : [];
  const total = SECTIONS.reduce((n, s) => n + count(s.key), 0);

  return (
    <div>
      <PageGuide
        id="verification"
        className="mb-6"
        title="Verifying student evidence"
        steps={[
          'Each item is a claim a student made — a certificate, publication, role or award — with any evidence they attached.',
          'Verified items count more towards a student’s score; rejected ones are excluded.',
          'Changes take effect on the next recompute, not instantly.',
        ]}
      />
      <h1 className="font-display text-2xl font-bold flex items-center gap-2">
        <BadgeCheck className="w-6 h-6 text-gold-400" /> Verification Queue
      </h1>
      <p className="text-sm text-cream/60 mt-1">
        Verify supporting evidence for research, experience, competitions and leadership before it counts toward a student&apos;s score.
        {total > 0 && <span className="text-gold-300"> · {total} pending</span>}
      </p>

      {/* Section tabs with counts */}
      <div className="mt-6 flex flex-wrap gap-2">
        {SECTIONS.map((s) => {
          const c = count(s.key);
          const on = active === s.key;
          return (
            <button
              key={s.key}
              onClick={() => setActive(s.key)}
              className={`flex items-center gap-2 px-3 py-2 rounded-lg text-sm transition-colors ${
                on ? 'bg-gold-400/15 text-gold-300' : 'bg-cream/5 text-cream/70 hover:text-white'
              }`}
            >
              <s.icon className="w-4 h-4" /> {s.label}
              <span className={`text-[11px] px-1.5 py-0.5 rounded-full ${c ? 'bg-gold-400/20 text-gold-200' : 'bg-cream/10 text-cream/50'}`}>
                {c}
              </span>
            </button>
          );
        })}
      </div>

      <div className="card mt-3 overflow-x-auto">
        <div className="data-head">
          <div className="col-span-5">Title</div>
          <div className="col-span-3">Type</div>
          <div className="col-span-2">Submitted</div>
          <div className="col-span-2 text-right">Decision</div>
        </div>
        {items.length === 0 ? (
          <EmptyState
            icon={current?.icon || BadgeCheck}
            title={`No pending ${current?.label?.toLowerCase() || ''} items`}
            description="Everything in this category has been reviewed."
          />
        ) : (
          items.map((item) => (
            <div key={item.id} className="data-row">
              <div className="col-span-5 min-w-0">
                <div className="font-medium truncate">{item.title || '—'}</div>
                <div className="text-[11px] text-cream/50 truncate">
                  {item.student_name || (item.student_id ? `Student ${String(item.student_id).slice(0, 8)}` : '')}
                </div>
              </div>
              <div className="col-span-3 text-sm text-cream/70 truncate">{item.type || '—'}</div>
              <div className="col-span-2 text-xs text-cream/50">
                {item.created_at ? new Date(item.created_at).toLocaleDateString() : '—'}
              </div>
              <div className="col-span-2 flex justify-end gap-1">
                <button
                  disabled={busy === `${current.key}:${item.id}`}
                  onClick={() => decide(current, item, 'verified')}
                  className="btn-ghost h-8 px-2 text-xs text-emerald-300"
                  title="Verify"
                >
                  <Check className="w-3.5 h-3.5" /> Verify
                </button>
                <button
                  disabled={busy === `${current.key}:${item.id}`}
                  onClick={() => decide(current, item, 'rejected')}
                  className="btn-ghost h-8 w-8 p-0 text-rose-300"
                  title="Reject"
                >
                  <X className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
