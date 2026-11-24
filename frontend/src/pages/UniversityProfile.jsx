import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { MapPin } from 'lucide-react';
import { universitiesService } from '@/services/universities.service';
import { rankingsService } from '@/services/rankings.service';
import { Loader } from '@/components/Loader';
import { StudentRow } from '@/components/StudentRow';
import { FieldChip } from '@/components/FieldChip';
import { BackLink } from '@/components/BackLink';
import { PageGuide } from '@/components/PageGuide';
import { fmtScore } from '@/utils/format';

export default function UniversityProfile() {
  const { slug } = useParams();
  const [uni, setUni] = useState(null);
  const [students, setStudents] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    universitiesService
      .get(slug)
      .then(async (u) => {
        setUni(u);
        const data = await rankingsService.students({
          scope: 'university',
          scope_key: u.id,
          limit: 60,
        });
        setStudents(data.rows || []);
      })
      .catch(() => setUni(null))
      .finally(() => setLoading(false));
  }, [slug]);

  if (loading) return <Loader label="Loading university…" />;
  if (!uni) return <div className="container-page py-12 text-white/50">Not found.</div>;

  return (
    <div className="container-page py-12">
      <BackLink className="mb-5" fallback="/universities" />
      <PageGuide
        id="university-profile"
        className="mb-6"
        title="How this university is ranked"
        steps={[
          'The headline figures come from the standardised scores of every approved student at this school.',
          'The table lists its top-ranked students; tap any of them for their full score breakdown.',
          'Studying here? Add your own results — every approved profile improves your school’s standing.',
        ]}
      />
      <div className="card p-6 flex flex-col md:flex-row md:items-center gap-6">
        <div className="w-14 h-14 rounded-xl bg-gold-400/15 grid place-content-center text-gold-400 text-2xl font-bold">
          {uni.short_name || uni.name?.[0]}
        </div>
        <div className="flex-1">
          <h1 className="font-display text-2xl font-extrabold">{uni.name}</h1>
          {uni.city && (
            <div className="flex items-center gap-1 text-sm text-white/40 mt-1">
              <MapPin className="w-3.5 h-3.5" /> {uni.city}, {uni.country}
            </div>
          )}
          <div className="flex flex-wrap gap-1.5 mt-3">
            {uni.field_tags?.map((t) => (
              <FieldChip key={t} name={t} slug={t} />
            ))}
          </div>
        </div>
        <div className="grid grid-cols-3 gap-6 text-center">
          <Stat label="Tier" value={uni.tier ?? '—'} />
          <Stat label="Avg" value={`${fmtScore(uni.avg_score)}`} />
          <Stat label="Top" value={fmtScore(uni.top_score)} />
        </div>
      </div>

      <div className="mt-8">
        <h2 className="font-display text-xl font-bold mb-3">Top Students</h2>
        <div className="card overflow-x-auto">
          <div className="data-head hidden sm:grid">
            <div className="col-span-1">Rank</div>
            <div className="col-span-4">Name</div>
            <div className="col-span-4">School · State</div>
            <div className="col-span-2">Discipline</div>
            <div className="col-span-1 text-right">Score</div>
          </div>
          {students.map((s, i) => (
            <StudentRow key={s.id} student={s} index={i} />
          ))}
        </div>
      </div>
    </div>
  );
}

function Stat({ label, value }) {
  return (
    <div>
      <div className="text-xl font-bold text-white tabular-nums">{value}</div>
      <div className="text-[11px] uppercase tracking-wider text-white/40">{label}</div>
    </div>
  );
}
