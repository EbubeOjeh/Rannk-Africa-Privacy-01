import { Clock, AlertTriangle } from 'lucide-react';
import { useAuth } from '@/hooks/useAuth';
import { isSchoolAdmin, isSuperAdmin } from '@/utils/constants';

/**
 * Renders a banner at the top of admin pages when a school admin's school is
 * still PENDING or has been REJECTED by the Super Admin. While pending, write
 * actions are blocked on the API side and the banner explains the state.
 */
export function PendingBanner() {
  const { role, user } = useAuth();
  if (!isSchoolAdmin(role) || isSuperAdmin(role)) return null;
  const status = user?.school_approval_status;
  if (!status || status === 'approved') return null;

  if (status === 'pending') {
    return (
      <div className="mb-6 rounded-xl border border-amber-400/30 bg-amber-500/10 px-4 py-3 flex items-start gap-3">
        <Clock className="w-5 h-5 text-amber-300 mt-0.5 shrink-0" />
        <div className="text-sm">
          <div className="font-semibold text-amber-200">
            {user?.school_name || 'Your school'} is awaiting RankAfrica approval.
          </div>
          <div className="text-amber-100/80 mt-0.5">
            You can view this dashboard, but uploading students, projects, and
            achievements is locked until a Super Admin approves your school.
          </div>
        </div>
      </div>
    );
  }
  if (status === 'rejected') {
    return (
      <div className="mb-6 rounded-xl border border-rose-400/30 bg-rose-500/10 px-4 py-3 flex items-start gap-3">
        <AlertTriangle className="w-5 h-5 text-rose-300 mt-0.5 shrink-0" />
        <div className="text-sm">
          <div className="font-semibold text-rose-200">
            {user?.school_name || 'Your school'}'s registration was rejected.
          </div>
          <div className="text-rose-100/80 mt-0.5">
            Please contact <a href="mailto:info@rankafrica.org" className="underline">info@rankafrica.org</a>.
          </div>
        </div>
      </div>
    );
  }
  return null;
}
