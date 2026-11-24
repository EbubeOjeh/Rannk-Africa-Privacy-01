import { useEffect, useRef, useState } from 'react';
import { Link } from 'react-router-dom';
import { Building2, Camera, CheckCircle2, Clock, KeyRound, Lock, Save, Trophy, XCircle } from 'lucide-react';
import toast from 'react-hot-toast';
import { authService } from '@/services/auth.service';
import { studentsService } from '@/services/students.service';
import { universitiesService } from '@/services/universities.service';
import { Loader } from '@/components/Loader';
import { useAuth } from '@/hooks/useAuth';
import { fmtScore, fmtRank } from '@/utils/format';

const PERMISSION_LABELS = {
  full_access: 'Full access',
  approve_schools: 'Approve schools',
  approve_recruiters: 'Approve recruiters',
  upload_transcripts: 'Upload transcripts',
  manage_students: 'Manage students',
  approve_students: 'Approve students',
  manage_cycles: 'Manage cycles',
  view_analytics: 'View analytics',
  manage_team: 'Manage team & roles',
};

const SCHOOL_ADMIN_ROLES = ['school_admin', 'university_admin'];

function initials(name = '') {
  return name.split(' ').filter(Boolean).slice(0, 2).map((p) => p[0]?.toUpperCase()).join('') || 'U';
}

export default function Profile() {
  const { user, setUser, permissions } = useAuth();
  const [name, setName] = useState(user?.name || '');
  const [busy, setBusy] = useState(false);
  const [uploading, setUploading] = useState(false);
  const fileRef = useRef(null);

  const save = async () => {
    if (name.trim().length < 2) return toast.error('Enter your full name.');
    setBusy(true);
    try {
      const updated = await authService.updateProfile({ name: name.trim() });
      setUser(updated);
      toast.success('Profile updated.');
    } catch (e) {
      toast.error(e?.response?.data?.error?.message || 'Update failed.');
    } finally {
      setBusy(false);
    }
  };

  const onPickAvatar = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploading(true);
    try {
      const updated = await authService.uploadAvatar(file);
      setUser(updated);
      toast.success('Photo updated.');
    } catch (err) {
      toast.error(err?.response?.data?.error?.message || 'Upload failed.');
    } finally {
      setUploading(false);
      if (fileRef.current) fileRef.current.value = '';
    }
  };

  return (
    <div className="max-w-4xl">
      <h1 className="font-display text-2xl font-bold">My Profile</h1>
      <p className="text-sm text-cream/60 mt-1">Update your photo and name. Your email can’t be changed.</p>

      <div className="card p-6 mt-6 space-y-6 max-w-2xl">
        {/* Avatar */}
        <div className="flex items-center gap-5">
          <div className="relative">
            <div className="w-20 h-20 rounded-full overflow-hidden bg-gold-400/15 grid place-content-center text-xl font-bold text-gold-300">
              {user?.avatar_url ? (
                <img src={user.avatar_url} alt={user.name} className="w-full h-full object-cover" />
              ) : (
                initials(user?.name)
              )}
            </div>
            <button
              type="button"
              onClick={() => fileRef.current?.click()}
              className="absolute -bottom-1 -right-1 btn-primary h-8 w-8 p-0 rounded-full"
              title="Upload photo"
            >
              <Camera className="w-4 h-4" />
            </button>
            <input ref={fileRef} type="file" accept="image/*" className="hidden" onChange={onPickAvatar} />
          </div>
          <div className="min-w-0">
            <p className="font-semibold text-white truncate">{user?.name}</p>
            <p className="text-sm text-cream/60 truncate">{user?.title || user?.company_role_name || 'Team member'}</p>
            {uploading && <p className="text-xs text-gold-300 mt-1">Uploading…</p>}
          </div>
        </div>

        {/* Full name */}
        <div>
          <label className="field-label">Full name</label>
          <input className="input" value={name} onChange={(e) => setName(e.target.value)} placeholder="Your full name" />
        </div>

        {/* Email (locked) */}
        <div>
          <label className="field-label">Email</label>
          <div className="relative">
            <input className="input pr-9 opacity-70 cursor-not-allowed" value={user?.email || ''} disabled />
            <Lock className="w-4 h-4 absolute right-3 top-1/2 -translate-y-1/2 text-cream/40" />
          </div>
        </div>

        {/* Role */}
        <div>
          <label className="field-label">Role</label>
          <p className="text-sm text-white">{user?.company_role_name || user?.title || user?.role?.replace('_', ' ')}</p>
          {permissions.length > 0 && (
            <div className="flex flex-wrap gap-1.5 mt-2">
              {permissions.map((p) => (
                <span key={p} className="pill bg-cream/10 text-cream/70">
                  {PERMISSION_LABELS[p] || p}
                </span>
              ))}
            </div>
          )}
        </div>

        <div className="flex flex-wrap gap-2 pt-2">
          <button onClick={save} disabled={busy} className="btn-primary">
            <Save className="w-4 h-4" /> {busy ? 'Saving…' : 'Save changes'}
          </button>
          <Link to="/admin/change-password" className="btn-ghost">
            <KeyRound className="w-4 h-4" /> Change password
          </Link>
        </div>
      </div>

      {SCHOOL_ADMIN_ROLES.includes(user?.role) && user?.university_id && (
        <SchoolSection user={user} />
      )}
    </div>
  );
}

const STATUS_BADGE = {
  approved: { cls: 'pill-success', icon: CheckCircle2, label: 'Verified' },
  pending: { cls: 'pill-pending', icon: Clock, label: 'Pending verification' },
  rejected: { cls: 'pill-danger', icon: XCircle, label: 'Rejected' },
};

const STUDENT_PILL = { approved: 'pill-success', pending: 'pill-pending', rejected: 'pill-danger' };

function SchoolSection({ user }) {
  const [school, setSchool] = useState(null);
  const [students, setStudents] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    Promise.all([
      universitiesService.get(user.university_id).catch(() => null),
      studentsService.list({ university_id: user.university_id, page_size: 100 }).catch(() => ({ items: [] })),
    ])
      .then(([s, list]) => {
        setSchool(s);
        setStudents(list.items || []);
      })
      .finally(() => setLoading(false));
  }, [user.university_id]);

  const status = user.school_approval_status || school?.approval_status || 'pending';
  const badge = STATUS_BADGE[status] || STATUS_BADGE.pending;
  const BadgeIcon = badge.icon;

  return (
    <div className="mt-8">
      <div className="flex items-center gap-2 flex-wrap">
        <h2 className="font-display text-xl font-bold">Your school</h2>
        <span className={badge.cls}>
          <BadgeIcon className="w-3.5 h-3.5" /> {badge.label}
        </span>
      </div>

      {status !== 'approved' && (
        <p className="text-sm text-cream/60 mt-2">
          Your school is awaiting verification. You can’t upload transcripts until a RankAfrica admin
          marks you <span className="text-emerald-300">Verified</span>.
        </p>
      )}

      {loading ? (
        <div className="mt-4"><Loader /></div>
      ) : (
        <>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mt-4">
            <StatCard icon={Building2} label="School" value={school?.name || user.school_name || '—'} small />
            <StatCard icon={Trophy} label="School rank" value={fmtRank(school?.overall_rank)} />
            <StatCard label="Avg score" value={fmtScore(school?.avg_score)} />
            <StatCard label="Students" value={school?.student_count ?? students.length} />
          </div>

          <h3 className="font-semibold text-white mt-8">Your students ({students.length})</h3>
          <div className="card mt-3 overflow-x-auto">
            <div className="data-head">
              <div className="col-span-1">#</div>
              <div className="col-span-5">Name</div>
              <div className="col-span-2">Score</div>
              <div className="col-span-2">Overall rank</div>
              <div className="col-span-2 text-right">Status</div>
            </div>
            {students.length === 0 ? (
              <div className="p-6 text-sm text-cream/60">No students uploaded yet.</div>
            ) : (
              students.map((s, i) => (
                <div key={s.id} className="data-row">
                  <div className="col-span-1 text-cream/50">{i + 1}</div>
                  <div className="col-span-5 truncate">
                    <Link to={`/students/${s.id}`} className="hover:text-gold-400">{s.full_name}</Link>
                  </div>
                  <div className="col-span-2 font-bold tabular-nums whitespace-nowrap">
                    {fmtScore(s.final_score ?? s.standardized_score)}<span className="text-cream/40 text-xs"> /100</span>
                  </div>
                  <div className="col-span-2 tabular-nums">{fmtRank(s.overall_rank)}</div>
                  <div className="col-span-2 text-right">
                    <span className={STUDENT_PILL[s.approval_status] || 'pill bg-cream/10 text-cream/60'}>
                      {s.approval_status}
                    </span>
                  </div>
                </div>
              ))
            )}
          </div>
        </>
      )}
    </div>
  );
}

function StatCard({ icon: Icon, label, value, small }) {
  return (
    <div className="card p-4">
      <div className="flex items-center gap-1.5 text-[11px] uppercase tracking-wider text-cream/50">
        {Icon && <Icon className="w-3.5 h-3.5" />} {label}
      </div>
      <div className={`font-bold text-white mt-1 ${small ? 'text-sm truncate' : 'text-xl'}`}>{value}</div>
    </div>
  );
}
