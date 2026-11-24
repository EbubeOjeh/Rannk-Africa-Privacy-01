import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  Search as SearchIcon,
  Bookmark,
  Briefcase,
  Building2,
  CheckCircle2,
  Clock,
  ArrowRight,
} from 'lucide-react';
import { StatCard } from '@/components/StatCard';
import { Loader } from '@/components/Loader';
import { PageGuide } from '@/components/PageGuide';
import { useAuth } from '@/hooks/useAuth';
import { employerService } from '@/services/employer.service';
import { opportunitiesService } from '@/services/opportunities.service';

export default function EmployerDashboard() {
  const { user } = useAuth();
  const [savedCount, setSavedCount] = useState(null);
  const [myOppsCount, setMyOppsCount] = useState(null);
  const [loading, setLoading] = useState(true);

  const approved = user?.approval_status === 'approved';

  useEffect(() => {
    let active = true;
    Promise.all([
      employerService.saved().catch(() => []),
      opportunitiesService.list().catch(() => []),
    ])
      .then(([saved, opps]) => {
        if (!active) return;
        setSavedCount(Array.isArray(saved) ? saved.length : 0);
        const mine = (Array.isArray(opps) ? opps : []).filter((o) => o.posted_by_id === user?.id);
        setMyOppsCount(mine.length);
      })
      .finally(() => active && setLoading(false));
    return () => {
      active = false;
    };
  }, [user?.id]);

  return (
    <div>
      <PageGuide
        id="employer-dashboard"
        className="mb-6"
        title="Your recruiter dashboard"
        steps={[
          'Search ranked students by field, university or score, and save the ones you want to shortlist.',
          'Post opportunities to put roles in front of every ranked student.',
          'Discovery excludes contact details. Applications share only separately authorized fields with their named recipient.',
        ]}
      />
      <p className="text-xs uppercase tracking-wider text-cream/50">Recruiter portal</p>
      <h1 className="font-display text-2xl sm:text-3xl font-bold mt-1">
        Welcome{user?.company_name ? `, ${user.company_name}` : user?.name ? `, ${user.name.split(' ')[0]}` : ''}
      </h1>
      <p className="text-sm text-cream/60 mt-2">
        Discover top-ranked students, shortlist candidates, and post opportunities.
      </p>

      <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4 mt-8">
        <StatCard
          icon={approved ? CheckCircle2 : Clock}
          label="Account status"
          title={approved ? 'Approved' : 'Pending approval'}
          accent={approved ? 'text-emerald-300' : 'text-amber-300'}
          sub={approved ? 'Approved recruiter discovery' : 'Recruiter access requires current approval'}
          index={0}
        />
        <StatCard
          icon={Bookmark}
          label="Saved candidates"
          title={loading ? '—' : String(savedCount ?? 0)}
          sub="Shortlisted students"
          index={1}
        />
        <StatCard
          icon={Briefcase}
          label="My opportunities"
          title={loading ? '—' : String(myOppsCount ?? 0)}
          sub="Posts you've created"
          index={2}
        />
      </div>

      {loading && <Loader label="Loading your portal…" />}

      <h2 className="font-display text-lg font-bold mt-10">Quick actions</h2>
      <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4 mt-4">
        <QuickLink to="/employer/search" icon={SearchIcon} title="Search students" desc="Filter by school, field & score" />
        <QuickLink to="/employer/saved" icon={Bookmark} title="Saved candidates" desc="Review your shortlist" />
        <QuickLink to="/employer/opportunities" icon={Briefcase} title="Opportunities" desc="Post & manage roles" />
        <QuickLink to="/employer/profile" icon={Building2} title="Company profile" desc="Keep your brand current" />
      </div>
    </div>
  );
}

function QuickLink({ to, icon: Icon, title, desc }) {
  return (
    <Link to={to} className="card p-5 group hover:border-gold-400/40 transition-colors">
      <span className="w-9 h-9 rounded-lg bg-gold-400/15 grid place-content-center text-gold-400">
        <Icon className="w-4 h-4" />
      </span>
      <div className="mt-3 font-semibold text-white flex items-center gap-1">
        {title}
        <ArrowRight className="w-3.5 h-3.5 text-cream/30 group-hover:text-gold-300 group-hover:translate-x-0.5 transition-all" />
      </div>
      <div className="text-xs text-cream/50 mt-1">{desc}</div>
    </Link>
  );
}
