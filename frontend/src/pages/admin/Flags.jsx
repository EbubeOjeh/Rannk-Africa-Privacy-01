import { useEffect, useState } from 'react';
import { Check, Flag as FlagIcon, ScanLine, ShieldAlert, X } from 'lucide-react';
import toast from 'react-hot-toast';
import { adminService } from '@/services/admin.service';
import { Loader } from '@/components/Loader';
import { EmptyState } from '@/components/EmptyState';
import { PageGuide } from '@/components/PageGuide';

const STATUSES = ['OPEN', 'confirmed', 'dismissed'];

// Severity → pill styling. Backend casing is unknown so we normalize.
const SEVERITY = {
  critical: 'pill bg-rose-500/20 text-rose-300',
  high: 'pill bg-rose-500/15 text-rose-300',
  medium: 'pill bg-amber-500/15 text-amber-200',
  low: 'pill bg-cream/10 text-cream/70',
};

const STATUS_PILL = {
  open: 'pill-pending',
  confirmed: 'pill-danger',
  dismissed: 'pill bg-cream/10 text-cream/60',
};

const sevClass = (s) => SEVERITY[String(s || '').toLowerCase()] || 'pill bg-cream/10 text-cream/70';
const statusClass = (s) => STATUS_PILL[String(s || '').toLowerCase()] || 'pill bg-cream/10 text-cream/60';
const isOpen = (s) => String(s || '').toLowerCase() === 'open';

export default function Flags() {
  const [flags, setFlags] = useState([]);
  const [stats, setStats] = useState(null);
  const [status, setStatus] = useState('OPEN');
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(null);
  const [scanId, setScanId] = useState('');
  const [scanning, setScanning] = useState(false);

  const load = (st = status) => {
    setLoading(true);
    Promise.all([
      adminService.flags(st ? { status: st } : {}),
      adminService.flagStats().catch(() => null),
    ])
      .then(([f, s]) => {
        setFlags(Array.isArray(f) ? f : []);
        setStats(s);
      })
      .catch(() => setFlags([]))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    load(status);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [status]);

  const resolve = async (flag, decision) => {
    let notes = null;
    if (decision === 'confirmed') {
      notes = prompt('Review notes (optional):') ?? null;
    }
    setBusy(flag.id);
    try {
      await adminService.resolveFlag(flag.id, { status: decision, review_notes: notes });
      toast.success(decision === 'confirmed' ? 'Flag confirmed.' : 'Flag dismissed.');
      setFlags((prev) => prev.filter((f) => f.id !== flag.id));
      adminService.flagStats().then(setStats).catch(() => {});
    } catch (err) {
      toast.error(err?.response?.data?.error?.message || 'Action failed.');
    } finally {
      setBusy(null);
    }
  };

  const scan = async (e) => {
    e.preventDefault();
    const id = scanId.trim();
    if (!id) return;
    setScanning(true);
    try {
      const found = await adminService.scanStudent(id);
      const n = Array.isArray(found) ? found.length : 0;
      toast.success(n ? `Scan complete — ${n} flag${n === 1 ? '' : 's'} raised.` : 'Scan complete — no issues found.');
      setScanId('');
      load();
    } catch (err) {
      toast.error(err?.response?.data?.error?.message || 'Scan failed.');
    } finally {
      setScanning(false);
    }
  };

  return (
    <div>
      <PageGuide
        id="flags"
        className="mb-6"
        title="AI integrity flags"
        steps={[
          'Flags are raised automatically where a submission looks duplicated, edited or implausible.',
          'Confirming a flag records it against the student; dismissing clears it.',
          'A flag is a prompt to look, not a verdict — always open the student’s profile before acting.',
        ]}
      />
      <h1 className="font-display text-2xl font-bold flex items-center gap-2">
        <ShieldAlert className="w-6 h-6 text-gold-400" /> Integrity Flags
      </h1>
      <p className="text-sm text-cream/60 mt-1">
        AI-assisted review queue. Confirm genuine integrity issues or dismiss false positives.
      </p>

      {/* Stat chips */}
      <div className="mt-5 flex flex-wrap gap-2">
        <StatChip label="Open" value={stats?.open} tone="amber" />
        <StatChip label="Confirmed" value={stats?.confirmed} tone="rose" />
        <StatChip label="Dismissed" value={stats?.dismissed} tone="muted" />
      </div>

      {/* Scan a student */}
      <form onSubmit={scan} className="card p-5 mt-6 flex flex-col sm:flex-row sm:items-end gap-3">
        <label className="block flex-1">
          <span className="field-label">Scan a student for integrity issues</span>
          <input
            className="input"
            placeholder="Student ID"
            value={scanId}
            onChange={(e) => setScanId(e.target.value)}
          />
        </label>
        <button type="submit" disabled={scanning || !scanId.trim()} className="btn-primary shrink-0">
          <ScanLine className="w-4 h-4" /> {scanning ? 'Scanning…' : 'Run scan'}
        </button>
      </form>

      {/* Status filter */}
      <div className="mt-6 flex items-center gap-2 flex-wrap">
        <span className="text-xs uppercase tracking-wider text-cream/50">Status</span>
        {STATUSES.map((s) => (
          <button
            key={s}
            onClick={() => setStatus(s)}
            className={`px-3 py-1 rounded-lg text-xs font-medium transition-colors ${
              status === s ? 'bg-gold-400/15 text-gold-300' : 'bg-cream/5 text-cream/70 hover:text-white'
            }`}
          >
            {s === 'OPEN' ? 'Open' : s.charAt(0).toUpperCase() + s.slice(1)}
          </button>
        ))}
      </div>

      <div className="card mt-3 overflow-x-auto">
        <div className="data-head">
          <div className="col-span-3">Student</div>
          <div className="col-span-3">Flag</div>
          <div className="col-span-1">Severity</div>
          <div className="col-span-3">Reason</div>
          <div className="col-span-2 text-right">Decision</div>
        </div>
        {loading ? (
          <Loader />
        ) : flags.length === 0 ? (
          <EmptyState
            icon={FlagIcon}
            title="No flags here"
            description="Nothing matches this status filter."
          />
        ) : (
          flags.map((f) => (
            <div key={f.id} className="data-row">
              <div className="col-span-3 min-w-0">
                <div className="font-medium truncate">{f.student_name || f.student_id?.slice(0, 8) || '—'}</div>
                <div className="text-[11px] text-cream/50 truncate">
                  {f.entity_type}
                  {f.ai_engine ? ` · ${f.ai_engine}` : ''}
                </div>
              </div>
              <div className="col-span-3 min-w-0">
                <div className="text-sm text-white truncate">{f.label || f.flag_type || '—'}</div>
                <div className="text-[11px] text-cream/40 truncate">
                  {f.created_at ? new Date(f.created_at).toLocaleDateString() : ''}
                </div>
              </div>
              <div className="col-span-1">
                <span className={sevClass(f.severity)}>{f.severity || '—'}</span>
              </div>
              <div className="col-span-3 text-sm text-cream/70 truncate" title={f.reason || ''}>
                {f.reason || f.details || '—'}
              </div>
              <div className="col-span-2 flex justify-end gap-1">
                {isOpen(f.status) ? (
                  <>
                    <button
                      disabled={busy === f.id}
                      onClick={() => resolve(f, 'confirmed')}
                      className="btn-ghost h-8 px-2 text-xs text-rose-300"
                      title="Confirm flag"
                    >
                      <Check className="w-3.5 h-3.5" /> Confirm
                    </button>
                    <button
                      disabled={busy === f.id}
                      onClick={() => resolve(f, 'dismissed')}
                      className="btn-ghost h-8 w-8 p-0 text-cream/60"
                      title="Dismiss flag"
                    >
                      <X className="w-3.5 h-3.5" />
                    </button>
                  </>
                ) : (
                  <span className={statusClass(f.status)}>{f.status}</span>
                )}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}

const TONES = {
  amber: 'text-amber-200 bg-amber-500/10 border-amber-500/20',
  rose: 'text-rose-300 bg-rose-500/10 border-rose-500/20',
  muted: 'text-cream/60 bg-cream/5 border-cream/10',
};

function StatChip({ label, value, tone = 'muted' }) {
  return (
    <div className={`flex items-center gap-2 px-3 py-1.5 rounded-lg border text-sm ${TONES[tone]}`}>
      <span className="font-bold tabular-nums">{value ?? 0}</span>
      <span className="text-xs uppercase tracking-wider opacity-80">{label}</span>
    </div>
  );
}
