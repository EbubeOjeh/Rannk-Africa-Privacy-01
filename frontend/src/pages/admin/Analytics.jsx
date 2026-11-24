import { useEffect, useState } from 'react';
import { StatCard } from '@/components/StatCard';
import { rankingsService } from '@/services/rankings.service';
import { Loader } from '@/components/Loader';
import { fmtNumber, fmtScore } from '@/utils/format';

export default function AdminAnalytics() {
  const [platform, setPlatform] = useState(null);
  const [dashboard, setDashboard] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([rankingsService.platformStats(), rankingsService.adminDashboard()])
      .then(([p, d]) => {
        setPlatform(p);
        setDashboard(d);
      })
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <Loader />;

  return (
    <div>
      <h1 className="font-display text-2xl font-bold">Analytics</h1>
      <p className="text-sm text-cream/60">Platform-wide and school-scoped insights, /100 scale.</p>

      <h2 className="mt-8 font-semibold">Platform</h2>
      <div className="mt-3 grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard label="Students" title={fmtNumber(platform?.total_students)} />
        <StatCard label="Schools" title={fmtNumber(platform?.total_universities)} />
        <StatCard label="Disciplines" title={fmtNumber(platform?.total_fields)} />
        <StatCard
          label="Top Score"
          title={`${fmtScore(platform?.top_student_score)} / 100`}
          accent="text-gold-400"
        />
      </div>

      <h2 className="mt-10 font-semibold">Your school</h2>
      <div className="mt-3 grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard label="Students" title={fmtNumber(dashboard?.students_total)} />
        <StatCard label="Avg Score" title={`${fmtScore(dashboard?.avg_score)} / 100`} />
        <StatCard label="Top Score" title={`${fmtScore(dashboard?.top_score)} / 100`} />
        <StatCard label="Elite (≥80)" title={fmtNumber(dashboard?.elite_count)} accent="text-gold-400" />
      </div>
    </div>
  );
}
