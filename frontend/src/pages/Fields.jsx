import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { GraduationCap, Building2 } from 'lucide-react';
import { fieldsService } from '@/services/fields.service';
import { rankingsService } from '@/services/rankings.service';
import { Loader } from '@/components/Loader';
import { StudentRow } from '@/components/StudentRow';
import { FieldCard } from '@/components/FieldCard';
import { EmptyState } from '@/components/EmptyState';
import { RankingsLocked } from '@/components/RankingsLocked';
import { EditableSection } from '@/components/EditableSection';
import { BackLink } from '@/components/BackLink';
import { PageGuide } from '@/components/PageGuide';
import { useRankingsRelease } from '@/hooks/useRankingsRelease';
import { usePageContent } from '@/hooks/usePageContent';

export default function Fields() {
  const { slug } = useParams();
  const [field, setField] = useState(null);
  const [fields, setFields] = useState([]);
  // Universities-first: selecting a field lands on the ranked universities in
  // that field; the student leaderboard is a secondary tab.
  const [tab, setTab] = useState('universities');
  const [students, setStudents] = useState([]);
  const [unis, setUnis] = useState([]);
  const [loading, setLoading] = useState(true);
  const release = useRankingsRelease();
  const c = usePageContent('fields');

  useEffect(() => {
    if (!slug) {
      fieldsService.list().then(setFields).finally(() => setLoading(false));
      return;
    }
    setLoading(true);
    fieldsService
      .get(slug)
      .then(async (f) => {
        setField(f);
        // Top universities in this field (avg score within the field, PRS §8)…
        const uniData = await rankingsService.universitiesByField(f.slug, 100);
        setUnis(uniData.rows || []);
        // …plus the student leaderboard for the secondary tab.
        const data = await rankingsService.students({
          scope: 'field',
          scope_key: f.slug,
          limit: 80,
        });
        setStudents(data.rows || []);
      })
      .catch(() => setField(null))
      .finally(() => setLoading(false));
  }, [slug]);

  if (loading) return <Loader />;

  if (!slug) {
    return (
      <div className="container-page py-12">
        <BackLink className="mb-5" />
        <PageGuide
          id="fields-list"
          className="mb-6"
          title="Browse the rankings by field of study"
          steps={[
            'Pick a discipline to see the universities that perform best in it, plus every student ranked within it.',
            'Scoring differs by field: Technology is judged largely on projects, while other fields are judged on an achievements and profile assessment.',
            'Your field is matched automatically from the course you enter when you register.',
          ]}
        />
        <EditableSection page="fields" id="header" title="Header">
          <h1 className="font-display text-2xl sm:text-3xl font-extrabold">{c.header.heading}</h1>
        </EditableSection>
        <div className="mt-6 grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4">
          {fields.map((f, i) => (
            <FieldCard key={f.id} field={f} index={i} />
          ))}
        </div>
      </div>
    );
  }

  if (!field) return <div className="container-page py-12 text-white/50">Field not found.</div>;

  return (
    <div className="container-page py-12">
      <BackLink className="mb-5" fallback="/fields" />
      <PageGuide
        id="field-detail"
        className="mb-6"
        title="Rankings inside this field"
        steps={[
          'The Universities tab ranks schools by how their students in this field perform; the Students tab is the individual leaderboard.',
          'Tap any row to open that university or student in full.',
          'Only approved, published profiles appear here.',
        ]}
      />
      <motion.div initial={{ opacity: 0, y: 6 }} animate={{ opacity: 1, y: 0 }} className="flex items-center gap-4">
        <div
          className="w-12 h-12 rounded-xl grid place-content-center"
          style={{ background: `${field.color || '#ffc740'}25` }}
        >
          <GraduationCap style={{ color: field.color || '#ffc740' }} className="w-6 h-6" />
        </div>
        <div>
          <p className="text-xs uppercase tracking-wider text-white/40">Field Rankings</p>
          <h1 className="font-display text-3xl font-extrabold mt-1">{field.name}</h1>
          {field.description && (
            <p className="text-sm text-white/50 mt-1">
              {field.description}
              {release.released ? ` · ${students.length} students ranked` : ''}
            </p>
          )}
        </div>
      </motion.div>

      {release.loading ? (
        <Loader />
      ) : !release.released ? (
        <RankingsLocked message={release.message} />
      ) : (
        <>
      <div className="mt-6 flex items-center gap-2">
        <TabButton active={tab === 'universities'} onClick={() => setTab('universities')} icon={Building2}>
          Universities
        </TabButton>
        <TabButton active={tab === 'students'} onClick={() => setTab('students')} icon={GraduationCap}>
          Students
        </TabButton>
      </div>

      <div className="mt-4 card overflow-x-auto">
        {tab === 'students' ? (
          <>
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
          </>
        ) : unis.length === 0 ? (
          <EmptyState
            title="No universities ranked yet"
            description="Rankings appear once students in this field are approved and published."
          />
        ) : (
          <div className="divide-y divide-white/5">
            {unis.map((u, i) => (
              <Link
                key={u.university_id}
                to={`/universities/${u.university_slug || u.university_id}`}
                className="flex flex-wrap items-center justify-between gap-2 px-4 py-3 hover:bg-white/[0.03] transition-colors"
              >
                <div className="flex items-center gap-3 min-w-0">
                  <span className={`shrink-0 w-7 h-7 rounded-md grid place-content-center text-xs font-bold ${medalClass(i)}`}>
                    {u.rank ?? i + 1}
                  </span>
                  <span className="text-white truncate hover:text-gold-400">{u.university_name}</span>
                  {u.university_state && (
                    <span className="hidden sm:inline text-xs text-cream/40 truncate">{u.university_state}</span>
                  )}
                </div>
                <div className="text-sm text-cream/70 whitespace-nowrap">
                  {u.student_count} {u.student_count === 1 ? 'student' : 'students'} · avg{' '}
                  <span className="text-white font-semibold">
                    {typeof u.avg_score === 'number' ? u.avg_score.toFixed(1) : u.avg_score}
                  </span>
                  <span className="text-cream/40">/100</span>
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>
        </>
      )}
    </div>
  );
}

function medalClass(i) {
  if (i === 0) return 'bg-gold-400 text-ink-text';      // gold
  if (i === 1) return 'bg-cream/70 text-ink-text';      // silver
  if (i === 2) return 'bg-amber-700/80 text-white';     // bronze
  return 'bg-white/5 text-cream/70';
}

function TabButton({ active, onClick, icon: Icon, children }) {
  return (
    <button
      onClick={onClick}
      className={`btn ${active ? 'bg-white text-ink-950' : 'bg-white/5 text-white/80 hover:bg-white/10'}`}
    >
      <Icon className="w-3.5 h-3.5" /> {children}
    </button>
  );
}
