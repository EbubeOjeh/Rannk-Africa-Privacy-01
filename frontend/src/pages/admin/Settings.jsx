import { useAuth } from '@/hooks/useAuth';
import { RankingsReleaseCard } from '@/components/RankingsReleaseCard';

export default function Settings() {
  const { user, can } = useAuth();
  return (
    <div className="max-w-xl">
      <h1 className="font-display text-2xl font-bold">Profile &amp; Settings</h1>
      <p className="text-sm text-white/50 mt-1">Account details on file.</p>

      <div className="card p-6 mt-6 space-y-4">
        <Row label="Name" value={user?.name} />
        <Row label="Email" value={user?.email} />
        <Row label="Role" value={user?.role?.replace('_', ' ')} />
        <Row label="University" value={user?.university_id || '—'} />
      </div>

      {can('manage_site') && <RankingsReleaseCard className="mt-6" />}

      <p className="text-xs text-white/30 mt-3">
        Password reset and 2FA flows are wired in the API and can be exposed here as needed.
      </p>
    </div>
  );
}

function Row({ label, value }) {
  return (
    <div className="flex items-center justify-between">
      <span className="text-xs uppercase tracking-wider text-white/40">{label}</span>
      <span className="text-sm text-white">{value || '—'}</span>
    </div>
  );
}
