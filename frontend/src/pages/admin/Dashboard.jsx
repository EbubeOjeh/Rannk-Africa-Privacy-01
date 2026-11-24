import { useEffect, useState } from 'react';
import { Trophy, Users, Sparkles, ClipboardCheck } from 'lucide-react';
import { StatCard } from '@/components/StatCard';
import { Loader } from '@/components/Loader';
import { RankingsReleaseCard } from '@/components/RankingsReleaseCard';
import { useAuth } from '@/hooks/useAuth';
import { rankingsService } from '@/services/rankings.service';
import { fmtScore, fmtNumber } from '@/utils/format';

export default function AdminDashboard() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const { can } = useAuth();

  useEffect(() => {
    rankingsService
      .adminDashboard()
      .then(setStats)
      .catch(() => setStats(null))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <Loader />;

  return (
    <div>
      <h1 className="font-display text-2xl font-bold">Dashboard</h1>
      <p className="text-sm text-cream/60 mt-1">
        Snapshot of registered students on the /100 RankAfrica index.
      </p>

      <div className="mt-6 grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard icon={Users} label="Students" title={fmtNumber(stats?.students_total)} sub="Submitted this cycle" />
        <StatCard icon={Trophy} label="Avg Score" title={`${fmtScore(stats?.avg_score)} / 100`} />
        <StatCard icon={Sparkles} label="Top Score" title={`${fmtScore(stats?.top_score)} / 100`} accent="text-gold-400" />
        <StatCard icon={ClipboardCheck} label="Pending Approval" title={fmtNumber(stats?.pending_approvals)} sub="Awaiting Super Admin" />
      </div>

      {/* Surfaced here, not just under Settings: staff can preview rankings
          even while they are hidden, so an admin otherwise has no way to know
          what the public actually sees. */}
      {can('manage_site') && <RankingsReleaseCard className="mt-8" />}

      <div className="mt-8 card p-6">
        <h2 className="font-semibold">Elite student count</h2>
        <p className="text-sm text-cream/60 mt-1">
          Students with a final score ≥ 80 / 100 — strong proxy for the top decile.
        </p>
        <div className="mt-4 font-display text-4xl font-extrabold text-gold-400">
          {fmtNumber(stats?.elite_count)}
        </div>
      </div>
    </div>
  );
}
