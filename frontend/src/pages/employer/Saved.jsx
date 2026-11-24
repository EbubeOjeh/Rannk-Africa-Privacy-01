import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Bookmark, Search as SearchIcon } from 'lucide-react';
import toast from 'react-hot-toast';
import { StudentResultCard } from '@/components/StudentResultCard';
import { Loader } from '@/components/Loader';
import { EmptyState } from '@/components/EmptyState';
import { PageGuide } from '@/components/PageGuide';
import { useAuth } from '@/hooks/useAuth';
import { employerService } from '@/services/employer.service';

export default function EmployerSaved() {
  const { user } = useAuth();
  const approved = user?.approval_status === 'approved';

  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [busyId, setBusyId] = useState(null);

  const refresh = () => {
    setLoading(true);
    employerService
      .saved()
      .then((data) => setItems(Array.isArray(data) ? data : []))
      .catch(() => setItems([]))
      .finally(() => setLoading(false));
  };

  useEffect(refresh, []);

  // On Saved, the toggle always means "remove" — drop the row optimistically.
  const remove = async (student) => {
    setBusyId(student.id);
    try {
      await employerService.unsave(student.id);
      setItems((list) => list.filter((s) => s.id !== student.id));
      toast.success('Removed from saved.');
    } catch (err) {
      toast.error(err?.response?.data?.error?.message || 'Could not remove.');
    } finally {
      setBusyId(null);
    }
  };

  return (
    <div>
      <PageGuide
        id="employer-saved"
        className="mb-6"
        title="Your shortlist"
        steps={[
          'Students you save from search collect here.',
          'Open any profile to see the full score breakdown and get in touch.',
          'Removing a student here does not notify them.',
        ]}
      />
      <div className="flex items-end justify-between gap-3 flex-wrap">
        <div>
          <p className="text-xs uppercase tracking-wider text-cream/50">Shortlist</p>
          <h1 className="font-display text-2xl sm:text-3xl font-bold mt-1 flex items-center gap-2">
            <Bookmark className="w-5 h-5 text-gold-400" /> Saved candidates
          </h1>
          <p className="text-sm text-cream/60 mt-2">
            {items.length} candidate{items.length === 1 ? '' : 's'} shortlisted.
          </p>
        </div>
        <Link to="/employer/search" className="btn-ghost text-xs">
          <SearchIcon className="w-3.5 h-3.5" /> Find more candidates
        </Link>
      </div>

      <div className="mt-6">
        {loading ? (
          <Loader label="Loading saved candidates…" />
        ) : items.length === 0 ? (
          <EmptyState
            title="No saved candidates yet"
            description="Save students from the search page to build your shortlist."
            icon={Bookmark}
            action={
              <Link to="/employer/search" className="btn-primary text-sm">
                <SearchIcon className="w-4 h-4" /> Search students
              </Link>
            }
          />
        ) : (
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {items.map((s, i) => (
              <StudentResultCard
                key={s.id}
                student={{ ...s, saved: true }}
                index={i}
                approved={approved}
                busy={busyId === s.id}
                onToggleSave={remove}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
