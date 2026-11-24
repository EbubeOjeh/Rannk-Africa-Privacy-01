import { Link } from 'react-router-dom';
import { GraduationCap, FlaskConical, Award, Target, Eye, ArrowRight } from 'lucide-react';
import { EditableSection } from '@/components/EditableSection';
import { BackLink } from '@/components/BackLink';
import { PageGuide } from '@/components/PageGuide';
import { usePageContent } from '@/hooks/usePageContent';

// Icons for the three-pipeline cards, matched by position.
const PIPELINE_ICONS = [GraduationCap, FlaskConical, Award];

export default function About() {
  const c = usePageContent('about');

  return (
    <div className="container-page py-16 max-w-3xl">
      <BackLink className="mb-5" />
      <PageGuide
        id="about"
        className="mb-6"
        title="What Rank Africa is"
        steps={[
          'We convert student results from different universities onto one standardised /100 index so they can be compared fairly.',
          'This page explains the scoring pipeline and what is coming next.',
          'To see the index in action, open Rankings from the menu.',
        ]}
        cta={{ to: '/rankings', label: 'View the rankings' }}
      />
      <EditableSection page="about" id="header" title="Header">
        <p className="text-xs uppercase tracking-wider text-gold-400">{c.header.eyebrow}</p>
        <h1 className="font-display text-3xl sm:text-4xl font-extrabold mt-2">{c.header.heading}</h1>
        <p className="text-cream/70 mt-4">{c.header.intro}</p>
      </EditableSection>

      <div className="mt-8 grid md:grid-cols-2 gap-4">
        <EditableSection page="about" id="mission" title="Mission">
          <Card icon={Target} title={c.mission.title}>{c.mission.body}</Card>
        </EditableSection>
        <EditableSection page="about" id="vision" title="Vision">
          <Card icon={Eye} title={c.vision.title}>{c.vision.body}</Card>
        </EditableSection>
      </div>

      <EditableSection page="about" id="pipelines" title="The three pipelines">
        <h2 className="mt-10 font-display text-xl font-bold">{c.pipelines.heading}</h2>
        <div className="mt-4 grid sm:grid-cols-3 gap-4">
          {c.pipelines.items.map((p, i) => {
            const Icon = PIPELINE_ICONS[i] || Award;
            return (
              <Card key={i} icon={Icon} title={p.title}>
                {p.body}
              </Card>
            );
          })}
        </div>
      </EditableSection>

      <EditableSection page="about" id="roadmap" title="Roadmap">
        <h2 className="mt-12 font-display text-xl font-bold">{c.roadmap.heading}</h2>
        <p className="text-sm text-cream/60 mt-1">{c.roadmap.subtitle}</p>
        <ol className="mt-5 relative border-l border-cream/10 ml-1">
          {c.roadmap.items.map((r, i) => (
            <li key={i} className="ml-5 pb-6 last:pb-0">
              <span
                className={`absolute -left-[7px] w-3.5 h-3.5 rounded-full border-2 border-ink-950 ${
                  r.state === 'done' ? 'bg-emerald-400' : r.state === 'active' ? 'bg-gold-400' : 'bg-cream/30'
                }`}
              />
              <p className="text-[11px] uppercase tracking-wider text-gold-400">{r.phase}</p>
              <h3 className="font-semibold text-white mt-0.5">{r.title}</h3>
              <p className="text-sm text-cream/70 mt-1 leading-relaxed">{r.body}</p>
            </li>
          ))}
        </ol>
      </EditableSection>

      <EditableSection
        page="about"
        id="teamCta"
        title="Team call-to-action"
        className="mt-10 card p-6 flex flex-wrap items-center justify-between gap-3"
      >
        <div>
          <h3 className="font-semibold text-white">{c.teamCta.heading}</h3>
          <p className="text-sm text-cream/60 mt-1">{c.teamCta.body}</p>
        </div>
        <Link to="/team" className="btn-primary">
          {c.teamCta.label} <ArrowRight className="w-4 h-4" />
        </Link>
      </EditableSection>

      <EditableSection page="about" id="footer" title="Footer note">
        <p className="text-xs text-cream/40 mt-10">{c.footer.note}</p>
      </EditableSection>
    </div>
  );
}

function Card({ icon: Icon, title, children }) {
  return (
    <div className="card p-5">
      <div className="w-9 h-9 rounded-lg bg-gold-400/15 grid place-content-center text-gold-400 mb-3">
        <Icon className="w-4 h-4" />
      </div>
      <h3 className="font-semibold text-white">{title}</h3>
      <p className="text-sm text-cream/70 mt-2 leading-relaxed">{children}</p>
    </div>
  );
}
