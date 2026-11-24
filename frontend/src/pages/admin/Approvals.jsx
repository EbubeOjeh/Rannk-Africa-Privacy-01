import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Check, Eye, X } from 'lucide-react';
import toast from 'react-hot-toast';
import { approvalsService } from '@/services/approvals.service';
import { Loader } from '@/components/Loader';
import { EmptyState } from '@/components/EmptyState';
import { PageGuide } from '@/components/PageGuide';
import { fmtScore } from '@/utils/format';

export default function Approvals() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(null);

  const refresh = () => {
    setLoading(true);
    approvalsService.pending().then(setItems).finally(() => setLoading(false));
  };
  useEffect(refresh, []);

  const decide = async (id, status) => {
    let notes = null;
    if (status === 'rejected') {
      notes = prompt('Reason for rejection (visible to the school admin):');
      if (notes === null) return;
    }
    setBusy(id);
    try {
      await approvalsService.set(id, { status, notes });
      toast.success(`Student ${status}.`);
      setItems(items.filter((s) => s.id !== id));
    } catch (err) {
      toast.error(err?.response?.data?.error?.message || 'Action failed.');
    } finally {
      setBusy(null);
    }
  };

  if (loading) return <Loader />;

  return (
    <div>
      <PageGuide
        id="approvals"
        className="mb-6"
        title="Approving students onto the leaderboard"
        steps={[
          'Approving a student marks their profile as reviewed — it does NOT publish them on its own.',
          'A student only becomes publicly visible once their submission cycle is set to PUBLISHED under Cycles.',
          'Rejecting keeps the account but removes the profile from the public leaderboard.',
        ]}
      />
      <h1 className="font-display text-2xl font-bold">Approval Queue</h1>
      <p className="text-sm text-cream/60 mt-1">
        Super Admin gate — only approved submissions appear on the public leaderboard
        once the cycle is published.
      </p>

      <div className="card mt-6 overflow-x-auto">
        <div className="data-head">
          <div className="col-span-4">Name</div>
          <div className="col-span-3">University</div>
          <div className="col-span-2">Cycle</div>
          <div className="col-span-1 text-right">Score</div>
          <div className="col-span-2 text-right">Decision</div>
        </div>
        {items.length === 0 ? (
          <EmptyState title="Nothing pending" description="All submitted students have been reviewed." />
        ) : (
          items.map((s) => (
            <div key={s.id} className="data-row">
              <div className="col-span-4 font-medium truncate">
                <Link to={`/students/${s.id}`} className="hover:text-gold-400" target="_blank" rel="noopener noreferrer">
                  {s.full_name}
                </Link>
              </div>
              <div className="col-span-3 text-sm text-cream/70 truncate">
                {s.university_id?.slice(0, 8) || '—'}
              </div>
              <div className="col-span-2 text-sm text-cream/70 truncate">
                {s.submission_cycle_id?.slice(0, 8) || '—'}
              </div>
              <div className="col-span-1 text-right font-bold tabular-nums whitespace-nowrap">
                {fmtScore(s.final_score ?? s.standardized_score)}
              </div>
              <div className="col-span-2 flex justify-end gap-1">
                <Link to={`/admin/students/${s.id}/edit`} className="btn-ghost h-8 w-8 p-0" title="Review">
                  <Eye className="w-3.5 h-3.5" />
                </Link>
                <button
                  disabled={busy === s.id}
                  onClick={() => decide(s.id, 'approved')}
                  className="btn-ghost h-8 w-8 p-0 text-emerald-300"
                  title="Approve"
                >
                  <Check className="w-3.5 h-3.5" />
                </button>
                <button
                  disabled={busy === s.id}
                  onClick={() => decide(s.id, 'rejected')}
                  className="btn-ghost h-8 w-8 p-0 text-rose-300"
                  title="Reject"
                >
                  <X className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
