import { useEffect, useMemo, useState } from 'react';
import { rankingsService } from '@/services/rankings.service';
import { Loader } from '@/components/Loader';
import { EmptyState } from '@/components/EmptyState';
import { useAuth } from '@/hooks/useAuth';
import { fmtScore } from '@/utils/format';

export default function DepartmentRankings() {
  const { user } = useAuth();
  const [students, setStudents] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    const params = { limit: 500, include_unpublished: true };
    if (user?.university_id) {
      params.scope = 'university';
      params.scope_key = user.university_id;
    }
    rankingsService
      .students(params)
      .then((d) => setStudents(d.rows || []))
      .catch(() => setStudents([]))
      .finally(() => setLoading(false));
  }, [user?.university_id]);

  const groups = useMemo(() => {
    const map = new Map();
    for (const s of students) {
      const score = s.final_score ?? s.standardized_score ?? 0;
      const key = s.field_name || 'Unassigned';
      if (!map.has(key)) map.set(key, { name: key, total: 0, sum: 0, top: 0 });
      const g = map.get(key);
      g.total += 1;
      g.sum += score;
      g.top = Math.max(g.top, score);
    }
    return [...map.values()]
      .map((g) => ({ ...g, avg: g.sum / Math.max(1, g.total) }))
      .sort((a, b) => b.avg - a.avg);
  }, [students]);

  if (loading) return <Loader />;
  if (groups.length === 0)
    return (
      <EmptyState
        title="No department data yet"
        description="Upload transcripts or add students to populate field rankings."
      />
    );

  return (
    <div>
      <h1 className="font-display text-2xl font-bold">Department / Field Rankings</h1>
      <p className="text-sm text-cream/60 mt-1">Average /100 score by discipline.</p>

      <div className="card mt-6 overflow-x-auto">
        <div className="data-head">
          <div className="col-span-1">#</div>
          <div className="col-span-5">Field</div>
          <div className="col-span-2">Students</div>
          <div className="col-span-2">Average</div>
          <div className="col-span-2 text-right">Top score</div>
        </div>
        {groups.map((g, i) => (
          <div key={g.name} className="data-row">
            <div className="col-span-1">
              <span className="inline-flex w-7 h-7 rounded-md bg-cream/5 items-center justify-center text-xs font-bold">
                {i + 1}
              </span>
            </div>
            <div className="col-span-5 text-white truncate">{g.name}</div>
            <div className="col-span-2 text-sm text-cream/70 truncate">{g.total} students</div>
            <div className="col-span-2 text-sm tabular-nums whitespace-nowrap">avg {fmtScore(g.avg)}</div>
            <div className="col-span-2 text-right tabular-nums font-semibold whitespace-nowrap">
              top {fmtScore(g.top)}<span className="text-cream/40 text-xs"> /100</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
