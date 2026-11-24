import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  Trophy,
  Building2,
  Users,
  ArrowRight,
  UserPlus,
  Search,
  ClipboardList,
  Gauge,
  Medal,
} from 'lucide-react';
import { StatCard } from '@/components/StatCard';
import { PageGuide } from '@/components/PageGuide';
import { LatestOpportunities, FeaturedEmployers } from '@/components/HomeSections';
import { reportsService } from '@/services/reports.service';
import { FieldCard } from '@/components/FieldCard';
import { EditableSection } from '@/components/EditableSection';
import { rankingsService } from '@/services/rankings.service';
import { fieldsService } from '@/services/fields.service';
import { usePageContent } from '@/hooks/usePageContent';
import { useRankingsRelease } from '@/hooks/useRankingsRelease';
import { fmtScore, fmtNumber } from '@/utils/format';

/**
 * The landing page at "/". This is the ONLY landing page: the old
 * launching-soon page and the duplicate /platform hub were retired at launch,
 * and both paths now redirect here.
 *
 * NOTE: the top-student / top-university cards name a real ranked student, and
 * the stats endpoint that backs them is public and un-gated. They are therefore
 * gated here on the admin "rankings release" switch, so this page never leaks a
 * leaderboard the admin has chosen to keep hidden.
 */
export default function Platform() {
  const [stats, setStats] = useState(null);
  const [fields, setFields] = useState([]);
  const [home, setHome] = useState(null);
  const c = usePageContent('platform');
  const { released, loading: releaseLoading } = useRankingsRelease();
  // Until the gate resolves, show the same neutral placeholder the stat cards
  // use while their data loads — rendering "Coming soon" first and then a real
  // name is what made the page look like it was swapping itself out.
  const gatedTitle = (value) => (releaseLoading ? '—' : released ? value || '—' : 'Coming soon');
  const gatedSub = (value) =>
    releaseLoading ? 'Loading…' : released ? value : 'Revealed when rankings are released';

  useEffect(() => {
    rankingsService.platformStats().then(setStats).catch(() => setStats(null));
    fieldsService.list().then(setFields).catch(() => setFields([]));
    // Live feed for the opportunities / employers strips. Purely additive —
    // both sections render nothing at all if this fails or comes back empty.
    reportsService.homepage().then(setHome).catch(() => setHome(null));
  }, []);

  return (
    <div>
      <section className="relative overflow-hidden">
        <div className="absolute inset-0 bg-hero-grid pointer-events-none" />
        <div className="container-page relative pt-20 pb-16 lg:pt-32 lg:pb-24">
          <EditableSection page="platform" id="hero" title="Hero">
            <motion.div
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6 }}
              className="max-w-2xl"
            >
              <p className="text-gold-400 font-semibold tracking-[0.18em] text-xs uppercase">
                {c.hero.eyebrow}
              </p>
              <h1 className="mt-3 font-display text-4xl sm:text-5xl lg:text-6xl font-extrabold leading-[1.05]">
                {c.hero.titleLead} <br />
                <span className="text-gold-400">{c.hero.titleHighlight}</span>
              </h1>
              <p className="mt-5 text-white/70 text-lg max-w-xl">{c.hero.subtitle}</p>
            </motion.div>
          </EditableSection>

          {/* The hero had no calls to action at all, which is why the
              leaderboard was undiscoverable. These are deliberately NOT
              conditional on the release switch: swapping the primary button
              once the switch resolved made the page visibly render twice.
              /rankings shows its own "coming soon" card (with its own CTAs)
              when rankings are hidden, so this never dead-ends. */}
          <div className="mt-8 flex flex-col sm:flex-row flex-wrap gap-3">
            <Link to="/rankings" className="btn-primary">
              See the full student rankings <ArrowRight className="w-4 h-4" />
            </Link>
            <Link to="/student-register" className="btn-outline">
              <UserPlus className="w-4 h-4" /> Create your student profile
            </Link>
          </div>
        </div>
      </section>

      <section className="container-page -mt-4 lg:-mt-10 relative grid sm:grid-cols-3 gap-4">
        <StatCard
          icon={Trophy}
          label="Top Ranked Student"
          title={gatedTitle(stats?.top_student_name)}
          sub={gatedSub(
            stats?.top_student_university
              ? `${stats.top_student_university} · ${fmtScore(stats.top_student_score)} / 100`
              : 'Awaiting evaluations'
          )}
          index={0}
        />
        <StatCard
          icon={Building2}
          label="Top University"
          title={gatedTitle(stats?.top_university_name)}
          sub={gatedSub(
            stats?.top_university_avg_score
              ? `Avg Score: ${fmtScore(stats.top_university_avg_score)} / 100 · ${stats.top_university_student_count} students`
              : 'Awaiting evaluations'
          )}
          index={1}
        />
        {/* The headline number is the door to the leaderboard. */}
        <Link to="/rankings" className="block rounded-2xl focus-visible:ring-2 focus-visible:ring-gold-400/60">
          <StatCard
            icon={Users}
            label="Total Students Ranked"
            title={fmtNumber(stats?.total_students)}
            sub="View the full leaderboard →"
            index={2}
            accent="text-gold-400"
          />
        </Link>
      </section>

      <div className="container-page mt-12">
        <PageGuide
          id="home"
          title="New to Rank Africa? Start here"
          steps={[
            'Rankings — the national leaderboard of every approved student, scored out of 100.',
            'Fields and Universities — the same rankings sliced by discipline or by school.',
            'Opportunities — roles, scholarships and competitions open to ranked students.',
            'Students: tap Join to build a profile. Recruiters: use Sign in → “Request recruiter access”.',
          ]}
          cta={{ to: '/rankings', label: 'See the rankings' }}
        />
      </div>

      {/* ── How it works — the visitor guide ──────────────────────────────
          No page on the site explained what the /100 score is; the only way
          to find out was to open an individual student profile. The weights
          below mirror the scoring engine, so they are intentionally NOT
          admin-editable copy. */}
      <section id="how-it-works" className="container-page mt-16 scroll-mt-24">
        <h2 className="font-display text-2xl font-bold">How RankAfrica works</h2>
        <p className="text-sm text-white/60 mt-1 max-w-2xl">
          One standardised score, so students from any Nigerian university can be compared fairly.
        </p>

        <div className="mt-6 grid grid-cols-1 sm:grid-cols-3 gap-4">
          {[
            {
              icon: ClipboardList,
              step: '1',
              title: 'Students build a profile',
              body: 'Register, add your CGPA and transcript, then your projects, achievements and experience.',
            },
            {
              icon: Gauge,
              step: '2',
              title: 'Everything is scored',
              body: 'Your CGPA is converted to a common 4.0 scale, and your work is assessed to produce a single /100 index.',
            },
            {
              icon: Medal,
              step: '3',
              title: 'You get ranked & discovered',
              body: 'Approved profiles join the public leaderboard, where recruiters search and invite candidates.',
            },
          ].map((s) => (
            <div key={s.step} className="card p-6">
              <div className="flex items-center gap-3">
                <span className="w-9 h-9 shrink-0 rounded-lg bg-gold-400/15 grid place-content-center text-gold-400">
                  <s.icon className="w-4 h-4" />
                </span>
                <span className="text-xs uppercase tracking-wider text-cream/40">Step {s.step}</span>
              </div>
              <h3 className="font-semibold mt-4">{s.title}</h3>
              <p className="text-sm text-cream/65 mt-2 leading-relaxed">{s.body}</p>
            </div>
          ))}
        </div>

        <div className="mt-4 card p-5">
          <p className="text-xs uppercase tracking-wider text-cream/40">What the /100 is made of</p>
          <div className="mt-3 grid gap-2 text-sm text-cream/75 sm:grid-cols-2">
            <p>
              <span className="text-white font-medium">Technology</span> — Academic 40 ·
              Project&nbsp;/&nbsp;Portfolio 40 · Achievements 20
            </p>
            <p>
              <span className="text-white font-medium">Every other field</span> — Academic 40 ·
              Achievements &amp; Profile 60
            </p>
          </div>
        </div>
      </section>

      {/* ── Audience split — the only place either group is addressed ── */}
      <section className="container-page mt-8 grid gap-4 sm:grid-cols-2">
        <div className="card p-6 flex flex-col">
          <span className="w-9 h-9 rounded-lg bg-gold-400/15 grid place-content-center text-gold-400">
            <UserPlus className="w-4 h-4" />
          </span>
          <h3 className="font-display text-lg font-bold mt-4">For students</h3>
          <p className="text-sm text-cream/65 mt-2 flex-1">
            Build your profile, get a standardised score, and be seen by recruiters hiring across
            Nigeria.
          </p>
          <Link to="/student-register" className="btn-primary mt-5 self-start">
            Create your profile <ArrowRight className="w-4 h-4" />
          </Link>
        </div>
        <div className="card p-6 flex flex-col">
          <span className="w-9 h-9 rounded-lg bg-gold-400/15 grid place-content-center text-gold-400">
            <Search className="w-4 h-4" />
          </span>
          <h3 className="font-display text-lg font-bold mt-4">For recruiters</h3>
          <p className="text-sm text-cream/65 mt-2 flex-1">
            Search ranked, verified talent by field, university and score — and shortlist the
            students you want to meet.
          </p>
          <Link to="/recruiter-register" className="btn-outline mt-5 self-start">
            Request recruiter access <ArrowRight className="w-4 h-4" />
          </Link>
        </div>
      </section>

      <section className="container-page mt-16">
        <EditableSection page="platform" id="browse" title="Browse by Field">
          <h2 className="font-display text-2xl font-bold">{c.browse.heading}</h2>
          <p className="text-sm text-white/60 mt-1">{c.browse.subtitle}</p>
        </EditableSection>
        <div className="mt-6 grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4">
          {fields.map((f, i) => (
            <FieldCard key={f.id} field={f} index={i} />
          ))}
        </div>
      </section>

      {/* Live feeds — each self-hides when its data is empty. */}
      <LatestOpportunities items={home?.latest_opportunities} />
      <FeaturedEmployers employers={home?.featured_employers} />

      {/* Mission & Vision */}
      <section className="container-page mt-16 grid md:grid-cols-2 gap-6">
        <EditableSection page="platform" id="mission" title="Mission" className="card p-7">
          <p className="text-xs uppercase tracking-[0.2em] text-gold-400">{c.mission.eyebrow}</p>
          <h2 className="font-display text-2xl font-bold mt-2">{c.mission.heading}</h2>
          <p className="text-cream/65 mt-3 leading-relaxed">{c.mission.body}</p>
        </EditableSection>
        <EditableSection page="platform" id="vision" title="Vision" className="card p-7">
          <p className="text-xs uppercase tracking-[0.2em] text-gold-400">{c.vision.eyebrow}</p>
          <h2 className="font-display text-2xl font-bold mt-2">{c.vision.heading}</h2>
          <p className="text-cream/65 mt-3 leading-relaxed">{c.vision.body}</p>
        </EditableSection>
      </section>
    </div>
  );
}
