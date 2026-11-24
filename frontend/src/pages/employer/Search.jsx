import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Filter, Search as SearchIcon, X, ChevronLeft, ChevronRight, Trophy } from 'lucide-react';
import toast from 'react-hot-toast';
import { StudentResultCard } from '@/components/StudentResultCard';
import { Loader } from '@/components/Loader';
import { EmptyState } from '@/components/EmptyState';
import { PageGuide } from '@/components/PageGuide';
import { useAuth } from '@/hooks/useAuth';
import { employerService } from '@/services/employer.service';
import { fieldsService } from '@/services/fields.service';
import { universitiesService } from '@/services/universities.service';

const PAGE_SIZE = 12;
const EMPTY_FILTERS = {
  q: '',
  university_id: '',
  field_id: '',
  min_score: '',
  max_score: '',
  graduation_year: '',
  skill: '',
};

export default function EmployerSearch() {
  const { user } = useAuth();
  const approved = user?.approval_status === 'approved';

  const [fields, setFields] = useState([]);
  const [universities, setUniversities] = useState([]);

  // `draft` holds the form; `filters` is the committed query (applied on submit).
  const [draft, setDraft] = useState(EMPTY_FILTERS);
  const [filters, setFilters] = useState(EMPTY_FILTERS);
  const [page, setPage] = useState(1);

  const [items, setItems] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [busyId, setBusyId] = useState(null);

  useEffect(() => {
    fieldsService.list().then(setFields).catch(() => setFields([]));
    universitiesService
      .list({ page_size: 100 })
      .then((d) => setUniversities(d.items || []))
      .catch(() => setUniversities([]));
  }, []);

  useEffect(() => {
    setLoading(true);
    const params = { page, page_size: PAGE_SIZE };
    Object.entries(filters).forEach(([k, v]) => {
      if (v !== '' && v != null) params[k] = v;
    });
    employerService
      .search(params)
      .then((data) => {
        setItems(data.items || []);
        setTotal(data.total || 0);
      })
      .catch(() => {
        setItems([]);
        setTotal(0);
      })
      .finally(() => setLoading(false));
  }, [filters, page]);

  const apply = (e) => {
    e?.preventDefault();
    setPage(1);
    setFilters(draft);
  };

  const clear = () => {
    setDraft(EMPTY_FILTERS);
    setFilters(EMPTY_FILTERS);
    setPage(1);
  };

  const setF = (k) => (e) => setDraft((d) => ({ ...d, [k]: e.target.value }));

  const toggleSave = async (student) => {
    setBusyId(student.id);
    try {
      if (student.saved) {
        await employerService.unsave(student.id);
        toast.success('Removed from saved.');
      } else {
        await employerService.save(student.id);
        toast.success('Candidate saved.');
      }
      setItems((list) =>
        list.map((s) => (s.id === student.id ? { ...s, saved: !s.saved } : s))
      );
    } catch (err) {
      toast.error(err?.response?.data?.error?.message || 'Action failed.');
    } finally {
      setBusyId(null);
    }
  };

  const activeFilters = Object.values(filters).filter((v) => v !== '').length;
  const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE));

  return (
    <div>
      <PageGuide
        id="employer-search"
        title="Finding candidates"
        steps={[
          'Filter by field, university, state or score band to narrow the ranked pool to the profiles you care about.',
          'Save a candidate to keep them on your shortlist, then contact them from their profile.',
          'Every score shown is the same standardised /100 index used on the public leaderboard.',
        ]}
      />
      <div className="flex items-end justify-between gap-3 flex-wrap">
        <div>
          <p className="text-xs uppercase tracking-wider text-cream/50">Talent search</p>
          <h1 className="font-display text-2xl sm:text-3xl font-bold mt-1">Search students</h1>
          <p className="text-sm text-cream/60 mt-2">
            {total} candidate{total === 1 ? '' : 's'} match your filters · standardised /100 index
          </p>
        </div>
        <Link to="/rankings" className="btn-ghost text-xs">
          <Trophy className="w-3.5 h-3.5" /> Public leaderboard
        </Link>
      </div>

      {!approved && (
        <div className="mt-6 rounded-xl border border-amber-400/30 bg-amber-500/10 px-4 py-3 text-sm text-amber-100/90">
          Your account is pending approval — search results are visible, but contact details stay
          locked until a RankAfrica admin approves you. You can still browse the{' '}
          <Link to="/rankings" className="underline text-amber-200">
            public ranking
          </Link>
          .
        </div>
      )}

      <form onSubmit={apply} className="card p-5 mt-6 space-y-4">
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-3">
          <label className="block sm:col-span-2 lg:col-span-3">
            <span className="field-label">Keyword</span>
            <div className="relative">
              <SearchIcon className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-cream/40" />
              <input
                className="input pl-9"
                value={draft.q}
                onChange={setF('q')}
                placeholder="Name, course, skill…"
              />
            </div>
          </label>

          <Select label="School" value={draft.university_id} onChange={setF('university_id')}>
            <option value="">All schools</option>
            {universities.map((u) => (
              <option key={u.id} value={u.id}>
                {u.name}
              </option>
            ))}
          </Select>

          <Select label="Field" value={draft.field_id} onChange={setF('field_id')}>
            <option value="">All fields</option>
            {fields.map((f) => (
              <option key={f.id} value={f.id}>
                {f.name}
              </option>
            ))}
          </Select>

          <label className="block">
            <span className="field-label">Graduation year</span>
            <input
              className="input"
              type="number"
              value={draft.graduation_year}
              onChange={setF('graduation_year')}
              placeholder="e.g. 2025"
            />
          </label>

          <label className="block">
            <span className="field-label">Min score</span>
            <input
              className="input"
              type="number"
              min="0"
              max="100"
              value={draft.min_score}
              onChange={setF('min_score')}
              placeholder="0"
            />
          </label>

          <label className="block">
            <span className="field-label">Max score</span>
            <input
              className="input"
              type="number"
              min="0"
              max="100"
              value={draft.max_score}
              onChange={setF('max_score')}
              placeholder="100"
            />
          </label>

          <label className="block">
            <span className="field-label">Skill</span>
            <input
              className="input"
              value={draft.skill}
              onChange={setF('skill')}
              placeholder="e.g. Python"
            />
          </label>
        </div>

        <div className="flex items-center justify-end gap-2">
          {activeFilters > 0 && (
            <button type="button" onClick={clear} className="btn-ghost text-xs">
              <X className="w-3.5 h-3.5" /> Clear {activeFilters}
            </button>
          )}
          <button type="submit" className="btn-primary text-sm">
            <Filter className="w-4 h-4" /> Apply filters
          </button>
        </div>
      </form>

      <div className="mt-6">
        {loading ? (
          <Loader label="Searching candidates…" />
        ) : items.length === 0 ? (
          <EmptyState
            title="No candidates match your filters"
            description="Try widening the score range or clearing a filter."
          />
        ) : (
          <>
            <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {items.map((s, i) => (
                <StudentResultCard
                  key={s.id}
                  student={s}
                  index={i}
                  approved={approved}
                  busy={busyId === s.id}
                  onToggleSave={toggleSave}
                />
              ))}
            </div>

            {totalPages > 1 && (
              <div className="flex items-center justify-center gap-3 mt-8">
                <button
                  className="btn-ghost text-xs"
                  disabled={page <= 1}
                  onClick={() => setPage((p) => Math.max(1, p - 1))}
                >
                  <ChevronLeft className="w-4 h-4" /> Prev
                </button>
                <span className="text-xs text-cream/60">
                  Page {page} of {totalPages}
                </span>
                <button
                  className="btn-ghost text-xs"
                  disabled={page >= totalPages}
                  onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                >
                  Next <ChevronRight className="w-4 h-4" />
                </button>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}

function Select({ label, value, onChange, children }) {
  return (
    <label className="block">
      <span className="field-label">{label}</span>
      <select className="input appearance-none cursor-pointer" value={value} onChange={onChange}>
        {children}
      </select>
    </label>
  );
}
