import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  GraduationCap,
  FlaskConical,
  Lightbulb,
  Users,
  Briefcase,
  Trophy,
  Award,
  Music,
  Bell,
  CheckCircle2,
  Clock,
  ShieldCheck,
  ArrowRight,
  Sparkles,
  ListChecks,
} from 'lucide-react';
import toast from 'react-hot-toast';
import { studentService } from '@/services/student.service';
import { Loader } from '@/components/Loader';
import { EmptyState } from '@/components/EmptyState';
import { PageGuide } from '@/components/PageGuide';
import { fmtScore, fmtRank } from '@/utils/format';

// Score components depend on the student's field model (from `scores.model`):
//   project model (Technology/Music) : Academic 40 + Project 40 + Achievements 20
//   profile model (all other fields) : Academic 40 + Profile Assessment 60
function componentsFor(scores) {
  const isProject = (scores?.model || 'project') === 'project';
  if (isProject) {
    return [
      { key: 'academic', label: 'Academic', icon: GraduationCap, max: 40 },
      { key: 'project', label: 'Project', icon: Lightbulb, max: 40 },
      { key: 'achievement', label: 'Achievements', icon: Award, max: 20 },
    ];
  }
  return [
    { key: 'academic', label: 'Academic', icon: GraduationCap, max: 40 },
    { key: 'profile', label: 'Achievements & Profile', icon: Sparkles, max: 60 },
  ];
}

const APPROVAL_PILL = {
  approved: 'pill-success',
  pending: 'pill-pending',
  rejected: 'pill-danger',
  not_submitted: 'pill-pending',
};

export default function StudentDashboard() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    studentService
      .dashboard()
      .then(setData)
      .catch((err) =>
        toast.error(err?.response?.data?.error?.message || 'Could not load your dashboard.')
      )
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <Loader label="Loading your dashboard…" />;
  if (!data) {
    return (
      <EmptyState
        title="Nothing to show yet"
        description="We couldn’t load your dashboard. Please refresh or try again shortly."
      />
    );
  }

  const scores = data.scores || {};
  const weights = scores.weights || {};
  const final = data.final_score ?? scores.final ?? 0;
  const completion = Math.round(data.profile_completion ?? 0);
  const status = data.approval_status || 'not_submitted';
  const badges = data.badges || [];
  const missing = data.missing_info || [];
  const recommendations = data.recommendations || [];
  const matches = data.opportunity_matches || [];

  return (
    <div className="space-y-8">
      <PageGuide
        id="student-dashboard"
        title="Your dashboard"
        steps={[
          'Your rank and score update whenever an admin re-runs the evaluation — they are not recalculated the moment you save.',
          'Profile completion below shows exactly what is still missing. The more complete and verified your profile, the higher you rank.',
          'Your profile only appears on the public leaderboard once an admin approves it and the current cycle is published.',
        ]}
        cta={{ to: '/student/profile', label: 'Complete your profile' }}
      />
      {/* Header */}
      <div className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <h1 className="font-display text-2xl font-bold">Your dashboard</h1>
          <p className="text-sm text-cream/60 mt-1">
            {data.field_name ? <>Field: <span className="text-cream/80">{data.field_name}</span></> : 'Track your standing and grow your score.'}
            {data.university_name ? <span className="text-cream/50"> · {data.university_name}</span> : null}
          </p>
        </div>
        <div className="flex items-center gap-2">
          <span className={`${APPROVAL_PILL[status] || 'pill-pending'}`}>
            <ShieldCheck className="w-3 h-3" /> {status.replace(/_/g, ' ')}
          </span>
          <Link to="/student/profile" className="btn-ghost text-xs">
            Edit profile <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>
      </div>

      {/* Score + ranks */}
      <div className="grid lg:grid-cols-3 gap-5">
        <motion.div
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          className="card p-6 lg:col-span-2"
        >
          <div className="flex items-baseline justify-between">
            <div>
              <p className="text-xs uppercase tracking-wider text-cream/50">Final score</p>
              <h2 className="font-display text-4xl font-extrabold mt-1">
                {fmtScore(final)}
                <span className="text-cream/40 text-lg font-semibold"> / 100</span>
              </h2>
            </div>
            {data.is_publicly_visible ? (
              <span className="pill-success">Live on leaderboard</span>
            ) : (
              <span className="pill-pending">Not yet public</span>
            )}
          </div>

          {/* Field-aware score breakdown */}
          <div className="mt-6 grid sm:grid-cols-2 xl:grid-cols-3 gap-3">
            {componentsFor(scores).map((c) => {
              const value = scores[c.key] ?? 0;
              const max = c.max;
              const Icon = c.icon;
              return (
                <div key={c.key} className="bg-cream/5 rounded-xl p-4">
                  <div className="flex items-center gap-2 text-[11px] uppercase tracking-wider text-cream/60">
                    <Icon className="w-3.5 h-3.5 text-gold-400" /> {c.label}
                  </div>
                  <div className="font-display text-xl font-extrabold mt-2 tabular-nums">
                    {fmtScore(value)}
                    {max != null && (
                      <span className="text-cream/40 text-xs font-semibold"> / {max}</span>
                    )}
                  </div>
                  {max != null && (
                    <div className="mt-2 h-1.5 bg-cream/10 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-gold-400 rounded-full"
                        style={{ width: `${Math.min(100, (value / max) * 100 || 0)}%` }}
                      />
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </motion.div>

        <div className="grid gap-5">
          <RankCard label="Overall rank" value={data.overall_rank} icon={Trophy} />
          <RankCard label="Field rank" value={data.field_rank} icon={FlaskConical} sub={data.field_name} />
          <RankCard label="University rank" value={data.university_rank} icon={GraduationCap} sub={data.university_name} />
        </div>
      </div>

      {/* Profile completion + verification + notifications */}
      <div className="grid md:grid-cols-3 gap-5">
        <div className="card p-5">
          <div className="flex items-center justify-between text-xs uppercase tracking-wider text-cream/50">
            <span className="flex items-center gap-2">
              <Sparkles className="w-3.5 h-3.5 text-gold-400" /> Profile completion
            </span>
            <span className="text-cream/80 font-semibold tabular-nums">{completion}%</span>
          </div>
          <div className="mt-3 h-2 bg-cream/10 rounded-full overflow-hidden">
            <motion.div
              initial={{ width: 0 }}
              animate={{ width: `${completion}%` }}
              transition={{ duration: 0.5 }}
              className="h-full bg-gold-400 rounded-full"
            />
          </div>
          {completion < 100 && (
            <Link to="/student/profile" className="text-xs text-gold-300 hover:underline mt-3 inline-block">
              Complete your profile →
            </Link>
          )}
        </div>

        <div className="card p-5">
          <div className="text-xs uppercase tracking-wider text-cream/50 flex items-center gap-2">
            <ShieldCheck className="w-3.5 h-3.5 text-gold-400" /> Verification
          </div>
          <div className="mt-3 flex items-center gap-4 text-sm">
            <span className="flex items-center gap-1.5 text-emerald-300">
              <CheckCircle2 className="w-4 h-4" /> {data.verified_items ?? 0} verified
            </span>
            <span className="flex items-center gap-1.5 text-amber-200">
              <Clock className="w-4 h-4" /> {data.pending_items ?? 0} pending
            </span>
          </div>
          <p className="text-[11px] text-cream/50 mt-2 capitalize">Status: {status.replace(/_/g, ' ')}</p>
        </div>

        <div className="card p-5">
          <div className="text-xs uppercase tracking-wider text-cream/50 flex items-center gap-2">
            <Bell className="w-3.5 h-3.5 text-gold-400" /> Notifications
          </div>
          <div className="font-display text-3xl font-extrabold mt-3 tabular-nums">
            {data.unread_notifications ?? 0}
          </div>
          <p className="text-[11px] text-cream/50 mt-1">unread updates</p>
        </div>
      </div>

      {/* Badges */}
      {badges.length > 0 && (
        <section>
          <h3 className="font-display text-lg font-bold mb-3">Your badges</h3>
          <div className="flex flex-wrap gap-2">
            {badges.map((b) => (
              <span
                key={b.badge_key}
                className="inline-flex items-center gap-1.5 rounded-full bg-gold-400/10 border border-gold-400/20 px-3 py-1.5 text-sm text-cream/90"
              >
                <span aria-hidden>{b.emoji}</span>
                {b.label}
              </span>
            ))}
          </div>
        </section>
      )}

      {/* Missing info checklist */}
      {missing.length > 0 && (
        <section className="card p-6">
          <h3 className="font-display text-lg font-bold flex items-center gap-2">
            <ListChecks className="w-4 h-4 text-gold-400" /> Complete your profile
          </h3>
          <p className="text-sm text-cream/60 mt-1">
            Add these to strengthen your ranking and unlock more opportunities.
          </p>
          <ul className="mt-4 space-y-2">
            {missing.map((item, i) => (
              <li key={i} className="flex items-start gap-2 text-sm text-cream/80">
                <span className="mt-1 w-3.5 h-3.5 shrink-0 rounded-full border border-gold-400/50" />
                {item}
              </li>
            ))}
          </ul>
          <Link to="/student/profile" className="btn-primary text-xs mt-5">
            Update profile <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </section>
      )}

      {/* Recommendations */}
      {recommendations.length > 0 && (
        <section>
          <h3 className="font-display text-lg font-bold mb-3">Recommendations</h3>
          <div className="grid sm:grid-cols-2 gap-4">
            {recommendations.map((r, i) => (
              <div key={i} className="card p-5">
                <div className="flex items-start gap-3">
                  <span className="w-8 h-8 shrink-0 rounded-lg bg-gold-400/15 grid place-content-center text-gold-400">
                    <Sparkles className="w-4 h-4" />
                  </span>
                  <div className="min-w-0">
                    <p className="font-semibold text-white">{r.title}</p>
                    {r.detail && <p className="text-sm text-cream/60 mt-1">{r.detail}</p>}
                    {r.action && (
                      <Link to={r.action} className="text-xs text-gold-300 hover:underline mt-2 inline-block">
                        Take action →
                      </Link>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </section>
      )}

      {/* Matched opportunities */}
      <section>
        <div className="flex items-center justify-between mb-3">
          <h3 className="font-display text-lg font-bold">Matched opportunities</h3>
          <Link to="/opportunities" className="text-xs text-gold-300 hover:underline">
            View all →
          </Link>
        </div>
        {matches.length === 0 ? (
          <div className="card">
            <EmptyState
              icon={Briefcase}
              title="No matches yet"
              description="As you complete your profile, RankAfrica will surface internships, hackathons and roles that fit you."
            />
          </div>
        ) : (
          <div className="card divide-y divide-cream/5">
            {matches.map((m) => (
              <div
                key={m.opportunity_id}
                className="flex items-center justify-between gap-4 px-5 py-4"
              >
                <div className="min-w-0">
                  <p className="font-medium text-white truncate">{m.title}</p>
                  <p className="text-xs text-cream/55 truncate">
                    {m.organization}
                    {m.type ? <span className="capitalize"> · {String(m.type).replace(/_/g, ' ')}</span> : null}
                  </p>
                  {m.reasoning && (
                    <p className="text-xs text-cream/45 mt-1 line-clamp-2">{m.reasoning}</p>
                  )}
                </div>
                <div className="text-right shrink-0">
                  <div className="font-display text-lg font-bold text-gold-300 tabular-nums">
                    {matchPercent(m.score)}%
                  </div>
                  <div className="text-[10px] uppercase tracking-wider text-cream/40">match</div>
                </div>
              </div>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}

// Opportunity match scores may arrive as a 0–1 fraction or an already-scaled
// 0–100 number; normalise both to a whole percentage.
function matchPercent(score) {
  const n = Number(score) || 0;
  return Math.round(n <= 1 ? n * 100 : n);
}

function RankCard({ label, value, sub, icon: Icon }) {
  return (
    <div className="card p-5">
      <div className="flex items-center gap-2 text-xs uppercase tracking-wider text-cream/50">
        <span className="w-7 h-7 rounded-md bg-white/5 grid place-content-center">
          <Icon className="w-4 h-4 text-gold-400" />
        </span>
        {label}
      </div>
      <div className="mt-3 font-display text-2xl font-bold tabular-nums">{fmtRank(value)}</div>
      {sub && <div className="text-xs text-cream/50 mt-1 truncate">{sub}</div>}
    </div>
  );
}
