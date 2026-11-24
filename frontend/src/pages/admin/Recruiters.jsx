import { useEffect, useState } from 'react';
import { Briefcase, Check, X } from 'lucide-react';
import toast from 'react-hot-toast';
import { recruitersService } from '@/services/recruiters.service';
import { Loader } from '@/components/Loader';
import { EmptyState } from '@/components/EmptyState';
import { PageGuide } from '@/components/PageGuide';

const PILLS = {
  pending: 'pill-pending',
  approved: 'pill-success',
  rejected: 'pill-danger',
};

export default function Recruiters() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(null);

  const load = () => {
    setLoading(true);
    recruitersService.list().then(setItems).catch(() => setItems([])).finally(() => setLoading(false));
  };
  useEffect(load, []);

  const decide = async (r, action) => {
    setBusy(r.id);
    try {
      await (action === 'approve' ? recruitersService.approve(r.id) : recruitersService.reject(r.id));
      toast.success(action === 'approve' ? 'Recruiter approved.' : 'Recruiter rejected.');
      load();
    } catch (err) {
      toast.error(err?.response?.data?.error?.message || 'Action failed.');
    } finally {
      setBusy(null);
    }
  };

  if (loading) return <Loader />;

  const pending = items.filter((r) => r.approval_status === 'pending');

  return (
    <div>
      <PageGuide
        id="recruiters"
        className="mb-6"
        title="Approving recruiter access"
        steps={[
          'Recruiters self-register and stay pending until approved here.',
          'Approved recruiters can search ranked students and see contact details, so verify the organisation first.',
          'Revoking access takes effect immediately.',
        ]}
      />
      <h1 className="font-display text-2xl font-bold">Recruiters & Employers</h1>
      <p className="text-sm text-cream/60 mt-1">
        Verify recruiter accounts. Only approved recruiters can view student contact details or message students.
        {pending.length > 0 && <span className="text-gold-300"> · {pending.length} awaiting review</span>}
      </p>

      <div className="card mt-6 overflow-x-auto">
        <div className="data-head">
          <div className="col-span-4">Recruiter</div>
          <div className="col-span-4">Organization</div>
          <div className="col-span-2">Status</div>
          <div className="col-span-2 text-right">Action</div>
        </div>
        {items.length === 0 ? (
          <EmptyState title="No recruiter requests yet" description="Recruiter sign-ups will appear here for review." />
        ) : (
          items.map((r) => (
            <div key={r.id} className="data-row">
              <div className="col-span-4 min-w-0">
                <div className="font-medium flex items-center gap-2 truncate">
                  <Briefcase className="w-4 h-4 text-gold-400 shrink-0" /> {r.name}
                </div>
                <div className="text-[11px] text-cream/50 truncate">{r.email}</div>
              </div>
              <div className="col-span-4 text-sm text-cream/80 truncate">{r.organization || '—'}</div>
              <div className="col-span-2">
                <span className={PILLS[r.approval_status] || 'pill bg-cream/10 text-cream/60'}>
                  {r.approval_status}
                </span>
              </div>
              <div className="col-span-2 flex justify-end gap-1">
                {r.approval_status !== 'approved' && (
                  <button disabled={busy === r.id} onClick={() => decide(r, 'approve')} className="btn-ghost text-xs text-emerald-300" title="Approve">
                    <Check className="w-3.5 h-3.5" /> Approve
                  </button>
                )}
                {r.approval_status !== 'rejected' && (
                  <button disabled={busy === r.id} onClick={() => decide(r, 'reject')} className="btn-ghost h-8 w-8 p-0 text-rose-300" title="Reject">
                    <X className="w-3.5 h-3.5" />
                  </button>
                )}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
