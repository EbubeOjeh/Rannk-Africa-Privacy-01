import { useEffect, useState } from 'react';
import { Archive, RefreshCw } from 'lucide-react';
import toast from 'react-hot-toast';
import { rankingsService } from '@/services/rankings.service';
import { Loader } from '@/components/Loader';
import { StudentRow } from '@/components/StudentRow';
import { PageGuide } from '@/components/PageGuide';
import { useAuth } from '@/hooks/useAuth';

export default function EvaluatedScores() {
  const { user, role } = useAuth();
  const [rows, setRows] = useState([]);
  const [loading, setLoading] = useState(true);
  const [recomputing, setRecomputing] = useState(false);

  const load = () => {
    setLoading(true);
    const params = { limit: 200, include_unpublished: true };
    if (user?.university_id) {
      params.scope = 'university';
      params.scope_key = user.university_id;
    }
    rankingsService
      .students(params)
      .then((d) => setRows(d.rows || []))
      .finally(() => setLoading(false));
  };
  useEffect(load, [user?.university_id]);

  const recompute = async () => {
    setRecomputing(true);
    try {
      await rankingsService.recompute();
      toast.success('Rankings recomputed.');
      load();
    } catch (e) {
      toast.error('Recompute failed.');
    } finally {
      setRecomputing(false);
    }
  };

  const publishSeason = async () => {
    const label = prompt('Archive the current rankings as a season.\nEnter a season label (e.g. 2025/26):');
    if (!label) return;
    try {
      const res = await rankingsService.publishSeason(label.trim());
      toast.success(`Archived "${res.label}" with ${res.total} students. Visible in the Rankings season selector.`);
    } catch (e) {
      toast.error(e?.response?.data?.error?.message || 'Could not archive season.');
    }
  };

  return (
    <div>
      <PageGuide
        id="evaluated-scores"
        className="mb-6"
        title="Scores and recomputing"
        steps={[
          'Recompute re-runs the scoring engine for every student and rewrites their ranks — run it after changing weights or approving a batch.',
          'Ties share a rank, so four students on the same score all show the same number.',
          'Students see their rank change after a recompute, so avoid running it needlessly.',
        ]}
      />
      <div className="flex items-center justify-between gap-3">
        <div>
          <h1 className="font-display text-2xl font-bold">Evaluated Scores</h1>
          <p className="text-sm text-cream/60 mt-1">
            Composite /100 scores from the three-pipeline engine (Academic + Project + Achievements).
          </p>
        </div>
        {role === 'super_admin' && (
          <div className="flex flex-wrap gap-2">
            <button onClick={recompute} disabled={recomputing} className="btn-ghost">
              <RefreshCw className={`w-3.5 h-3.5 ${recomputing ? 'animate-spin' : ''}`} />
              {recomputing ? 'Recomputing…' : 'Recompute rankings'}
            </button>
            <button onClick={publishSeason} className="btn-ghost" title="Freeze current rankings as a season">
              <Archive className="w-3.5 h-3.5" /> Archive season
            </button>
          </div>
        )}
      </div>

      <div className="mt-6 card overflow-x-auto">
        <div className="data-head">
          <div className="col-span-1">Rank</div>
          <div className="col-span-4">Name</div>
          <div className="col-span-4">School · State</div>
          <div className="col-span-2">Discipline</div>
          <div className="col-span-1 text-right">Score</div>
        </div>
        {loading ? <Loader /> : rows.map((s, i) => <StudentRow key={s.id} student={s} index={i} />)}
      </div>
    </div>
  );
}
