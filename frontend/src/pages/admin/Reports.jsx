import { useEffect, useState } from 'react';
import { Printer, FileBarChart } from 'lucide-react';
import { adminService } from '@/services/admin.service';
import { StatCard } from '@/components/StatCard';
import { Loader } from '@/components/Loader';
import { EmptyState } from '@/components/EmptyState';
import { fmtNumber, fmtScore } from '@/utils/format';

// Humanize a snake_case / camelCase key for display, e.g. "top_score" → "Top Score".
const humanize = (k) =>
  String(k)
    .replace(/[_-]+/g, ' ')
    .replace(/([a-z])([A-Z])/g, '$1 $2')
    .replace(/\b\w/g, (c) => c.toUpperCase());

const isNum = (v) => typeof v === 'number' && Number.isFinite(v);
const fmtVal = (v) => (isNum(v) ? fmtNumber(v) : v == null ? '—' : String(v));

export default function Reports() {
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    adminService
      .platformReport()
      .then((d) => setReport(d || {}))
      .catch(() => setReport({}))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <Loader />;

  const totals = report?.totals && typeof report.totals === 'object' ? report.totals : {};
  const dist =
    report?.score_distribution && typeof report.score_distribution === 'object'
      ? report.score_distribution
      : {};
  const topStudents = Array.isArray(report?.top_students) ? report.top_students : [];
  const topUnis = Array.isArray(report?.top_universities) ? report.top_universities : [];

  const totalEntries = Object.entries(totals);
  const distEntries = Object.entries(dist).filter(([, v]) => isNum(v));
  const distMax = distEntries.reduce((m, [, v]) => Math.max(m, v), 0) || 1;
  const empty = !totalEntries.length && !distEntries.length && !topStudents.length && !topUnis.length;

  return (
    <div className="print:text-black">
      <div className="flex items-start justify-between gap-4 print:block">
        <div>
          <h1 className="font-display text-2xl font-bold flex items-center gap-2">
            <FileBarChart className="w-6 h-6 text-gold-400" /> Platform Report
          </h1>
          <p className="text-sm text-cream/60 mt-1">
            A snapshot of platform-wide performance. Generated {new Date().toLocaleString()}.
          </p>
        </div>
        <button onClick={() => window.print()} className="btn-ghost shrink-0 print:hidden">
          <Printer className="w-4 h-4" /> Print / export
        </button>
      </div>

      {empty ? (
        <div className="card mt-6">
          <EmptyState
            icon={FileBarChart}
            title="No report data yet"
            description="Once students are scored and ranked, platform metrics will appear here."
          />
        </div>
      ) : (
        <>
          {/* Totals as stat cards */}
          {totalEntries.length > 0 && (
            <>
              <h2 className="mt-8 font-semibold">Totals</h2>
              <div className="mt-3 grid grid-cols-2 lg:grid-cols-4 gap-4">
                {totalEntries.map(([k, v], i) => (
                  <StatCard key={k} label={humanize(k)} title={fmtVal(v)} index={i} />
                ))}
              </div>
            </>
          )}

          {/* Score distribution as labeled bars */}
          {distEntries.length > 0 && (
            <>
              <h2 className="mt-10 font-semibold">Score distribution</h2>
              <div className="card p-6 mt-3 space-y-3">
                {distEntries.map(([k, v]) => (
                  <div key={k}>
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-cream/70">{humanize(k)}</span>
                      <span className="tabular-nums font-medium">{fmtNumber(v)}</span>
                    </div>
                    <div className="mt-1 h-2 rounded-full bg-cream/5 overflow-hidden">
                      <div
                        className="h-full rounded-full bg-gold-400"
                        style={{ width: `${Math.max(2, (v / distMax) * 100)}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </>
          )}

          {/* Top students */}
          {topStudents.length > 0 && (
            <RankTable
              title="Top students"
              rows={topStudents}
              nameKey={['full_name', 'name', 'student_name']}
              subKey={['university_name', 'university', 'field_name']}
            />
          )}

          {/* Top universities */}
          {topUnis.length > 0 && (
            <RankTable
              title="Top universities"
              rows={topUnis}
              nameKey={['name', 'university_name']}
              subKey={['country', 'students_count', 'student_count']}
            />
          )}
        </>
      )}
    </div>
  );
}

const pick = (obj, keys) => {
  for (const k of keys) if (obj?.[k] != null && obj[k] !== '') return obj[k];
  return null;
};
const pickScore = (obj) =>
  obj?.final_score ?? obj?.avg_score ?? obj?.score ?? obj?.standardized_score ?? null;

function RankTable({ title, rows, nameKey, subKey }) {
  return (
    <>
      <h2 className="mt-10 font-semibold">{title}</h2>
      <div className="card mt-3 overflow-x-auto">
        <div className="data-head">
          <div className="col-span-1">#</div>
          <div className="col-span-6">Name</div>
          <div className="col-span-3">Detail</div>
          <div className="col-span-2 text-right">Score</div>
        </div>
        {rows.map((r, i) => (
          <div key={r.id || i} className="data-row">
            <div className="col-span-1">
              <span className="inline-flex w-7 h-7 rounded-md bg-cream/5 items-center justify-center text-xs font-bold">
                {i + 1}
              </span>
            </div>
            <div className="col-span-6 text-white truncate">{pick(r, nameKey) || '—'}</div>
            <div className="col-span-3 text-sm text-cream/60 truncate">{fmtVal(pick(r, subKey)) || '—'}</div>
            <div className="col-span-2 text-right tabular-nums font-semibold whitespace-nowrap">
              {pickScore(r) != null ? fmtScore(pickScore(r)) : '—'}
              <span className="text-cream/40 text-xs"> /100</span>
            </div>
          </div>
        ))}
      </div>
    </>
  );
}
