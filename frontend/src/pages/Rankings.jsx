import { useEffect, useMemo, useState } from 'react';
import { Filter, SlidersHorizontal, X } from 'lucide-react';
import { motion } from 'framer-motion';
import { SearchBar } from '@/components/SearchBar';
import { StudentRow } from '@/components/StudentRow';
import { Loader } from '@/components/Loader';
import { EmptyState } from '@/components/EmptyState';
import { RankingsLocked } from '@/components/RankingsLocked';
import { BackLink } from '@/components/BackLink';
import { PageGuide } from '@/components/PageGuide';
import { EditableSection } from '@/components/EditableSection';
import { useDebounce } from '@/hooks/useDebounce';
import { useRankingsRelease } from '@/hooks/useRankingsRelease';
import { usePageContent } from '@/hooks/usePageContent';
import { rankingsService } from '@/services/rankings.service';
import { fieldsService } from '@/services/fields.service';
import { universitiesService } from '@/services/universities.service';
import { NIGERIAN_STATES } from '@/utils/constants';

// How many rows we pull in one go. The API caps at 500; when the response is
// exactly this length the list is truncated, so the count is shown as "N+".
const PAGE_LIMIT = 500;

export default function Rankings() {
  const [students, setStudents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showFilters, setShowFilters] = useState(false);
  const [fields, setFields] = useState([]);
  const [universities, setUniversities] = useState([]);
  const [query, setQuery] = useState('');
  const [field, setField] = useState('');
  const [universityId, setUniversityId] = useState('');
  const [state, setState] = useState('');
  const [minScore, setMinScore] = useState('');
  const [maxScore, setMaxScore] = useState('');
  const [sort, setSort] = useState('score');
  const [season, setSeason] = useState('live');
  const [seasons, setSeasons] = useState([]);

  const debouncedQ = useDebounce(query, 200);
  const isLive = season === 'live';
  const release = useRankingsRelease();
  const c = usePageContent('rankings');

  useEffect(() => {
    fieldsService.list().then(setFields).catch(() => setFields([]));
    universitiesService
      .list({ page_size: 100 })
      .then((d) => setUniversities(d.items || []))
      .catch(() => setUniversities([]));
    rankingsService.seasons().then(setSeasons).catch(() => setSeasons([]));
  }, []);

  useEffect(() => {
    setLoading(true);
    // Archived season → load the frozen snapshot (filters don't apply).
    if (!isLive) {
      rankingsService
        .season(season)
        .then((data) => setStudents(data.rows || []))
        .catch(() => setStudents([]))
        .finally(() => setLoading(false));
      return;
    }
    const params = { limit: PAGE_LIMIT, sort };
    if (universityId) {
      params.scope = 'university';
      params.scope_key = universityId;
    } else if (field) {
      params.scope = 'field';
      params.scope_key = field;
    }
    if (state) params.state = state;
    if (minScore !== '') params.min_score = Number(minScore);
    if (maxScore !== '') params.max_score = Number(maxScore);
    rankingsService
      .students(params)
      .then((data) => setStudents(data.rows || []))
      .catch(() => setStudents([]))
      .finally(() => setLoading(false));
  }, [field, universityId, state, minScore, maxScore, sort, season, isLive]);

  const filtered = useMemo(() => {
    if (!debouncedQ) return students;
    const q = debouncedQ.toLowerCase();
    return students.filter(
      (s) =>
        s.full_name?.toLowerCase().includes(q) ||
        s.university_name?.toLowerCase().includes(q)
    );
  }, [students, debouncedQ]);

  const activeFilters = [field, universityId, state, minScore, maxScore].filter(Boolean).length;

  const clear = () => {
    setField('');
    setUniversityId('');
    setState('');
    setMinScore('');
    setMaxScore('');
    setQuery('');
  };

  return (
    <div className="container-page py-12">
      <BackLink className="mb-5" />
      <EditableSection page="rankings" id="header" title="Header">
        <motion.div initial={{ opacity: 0, y: 6 }} animate={{ opacity: 1, y: 0 }}>
          <p className="text-xs uppercase tracking-wider text-cream/50">{c.header.eyebrow}</p>
          <h1 className="font-display text-3xl sm:text-4xl font-extrabold mt-1">{c.header.heading}</h1>
          {release.released && (
            <>
              <p className="text-sm text-cream/70 mt-2 max-w-2xl">
                {isLive
                  ? 'Every approved student, across all universities and disciplines, ranked on a single standardised /100 index.'
                  : `The frozen ${season} season leaderboard.`}
              </p>
              <p className="text-sm text-cream/50 mt-1">
                {students.length}
                {students.length === PAGE_LIMIT ? '+' : ''}{' '}
                {isLive ? 'ranked students' : `students · ${season} archive`}
              </p>
            </>
          )}
        </motion.div>
      </EditableSection>

      <PageGuide
        id="rankings"
        className="mt-6"
        title="This is the national student leaderboard"
        steps={[
          'Every approved student is scored out of 100 and listed highest first. Students on the same score share the same rank.',
          'Search by name, or use the filters to narrow by discipline, university, state or score range. On a phone the filters sit behind the “Filters & sorting” button.',
          'Tap any student to open their profile and see exactly how their score was built.',
        ]}
        cta={{ to: '/student-register', label: 'Get ranked — create your profile' }}
      />

      {release.loading ? (
        <Loader label="Loading…" />
      ) : !release.released ? (
        <RankingsLocked message={release.message} />
      ) : (
        <>
      <div className="mt-8">
        {/* Search is always visible; the rest collapses behind a toggle on a
            phone so the leaderboard itself starts near the top of the screen
            instead of below ~400px of stacked selects. `sm:contents` makes the
            wrapper vanish from the layout at sm+, restoring the flat flex row. */}
        <div className="flex flex-col gap-3 sm:flex-row sm:flex-wrap sm:items-center">
          <SearchBar value={query} onChange={setQuery} />

          <button
            type="button"
            onClick={() => setShowFilters((v) => !v)}
            className="btn-ghost sm:hidden justify-between"
            aria-expanded={showFilters}
          >
            <span className="inline-flex items-center gap-2">
              <SlidersHorizontal className="w-4 h-4" />
              Filters &amp; sorting
            </span>
            {activeFilters > 0 && (
              <span className="pill bg-gold-400/20 text-gold-300">{activeFilters}</span>
            )}
          </button>

          <div
            className={`${showFilters ? 'flex' : 'hidden'} flex-col gap-3 sm:contents`}
          >
          {seasons.length > 0 && (
            <Select
              label="Season"
              value={season}
              onChange={setSeason}
              options={[
                { id: 'live', label: 'Live (current)' },
                ...seasons.map((s) => ({ id: s.label, label: `${s.label} (archived)` })),
              ]}
            />
          )}
          {isLive && (
            <>
              <Select
                label="Discipline"
                value={field}
                onChange={(v) => setField(v)}
                options={[{ id: '', label: 'All disciplines' }, ...fields.map((f) => ({ id: f.slug, label: f.name }))]}
              />
              <Select
                label="School"
                value={universityId}
                onChange={(v) => setUniversityId(v)}
                options={[
                  { id: '', label: 'All schools' },
                  ...universities.map((u) => ({ id: u.id, label: u.name })),
                ]}
              />
              <Select
                label="State"
                value={state}
                onChange={(v) => setState(v)}
                options={[{ id: '', label: 'All states' }, ...NIGERIAN_STATES.map((s) => ({ id: s, label: s }))]}
              />
              <div className="flex items-center gap-2 text-sm">
                <span className="text-cream/60 shrink-0">Score</span>
                <input
                  type="number"
                  min="0" max="100"
                  placeholder="min"
                  value={minScore}
                  onChange={(e) => setMinScore(e.target.value)}
                  className="input w-full sm:w-20"
                />
                <span className="text-cream/40 shrink-0">→</span>
                <input
                  type="number"
                  min="0" max="100"
                  placeholder="max"
                  value={maxScore}
                  onChange={(e) => setMaxScore(e.target.value)}
                  className="input w-full sm:w-20"
                />
              </div>
              <Select
                label="Sort"
                value={sort}
                onChange={setSort}
                options={[
                  { id: 'score', label: 'Score (high → low)' },
                  { id: 'name', label: 'Name (A → Z)' },
                ]}
              />
              {activeFilters > 0 && (
                <button onClick={clear} className="btn-ghost text-xs">
                  <X className="w-3.5 h-3.5" /> Clear {activeFilters}
                </button>
              )}
            </>
          )}
          </div>
        </div>
      </div>

      <div className="mt-6 card overflow-x-auto">
        {/* Hidden on phones — StudentRow renders a self-labelling card there. */}
        <div className="data-head hidden sm:grid">
          <div className="col-span-1">Rank</div>
          <div className="col-span-4">Name</div>
          <div className="col-span-4">School · State</div>
          <div className="col-span-2">Discipline</div>
          <div className="col-span-1 text-right">Score</div>
        </div>
        {loading ? (
          <Loader label="Loading leaderboard…" />
        ) : filtered.length === 0 ? (
          <EmptyState
            title="No students match your filters"
            description="Try widening your search or clearing the field filter."
          />
        ) : (
          filtered.map((s, i) => <StudentRow key={s.id} student={s} index={i} />)
        )}
      </div>
        </>
      )}
    </div>
  );
}

function Select({ label, value, onChange, options }) {
  return (
    <div className="relative w-full sm:w-auto">
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="input pr-8 appearance-none cursor-pointer"
        title={label}
      >
        {options.map((o) => (
          <option key={o.id} value={o.id}>
            {o.label}
          </option>
        ))}
      </select>
      <Filter className="w-3.5 h-3.5 absolute right-2 top-1/2 -translate-y-1/2 text-cream/40 pointer-events-none" />
    </div>
  );
}
