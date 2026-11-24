import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { teamService } from '@/services/team.service';
import { Loader } from '@/components/Loader';
import { EditableSection } from '@/components/EditableSection';
import { BackLink } from '@/components/BackLink';
import { PageGuide } from '@/components/PageGuide';
import { usePageContent } from '@/hooks/usePageContent';

function initials(name = '') {
  return name.split(' ').filter(Boolean).slice(0, 2).map((p) => p[0]?.toUpperCase()).join('') || 'RA';
}

export default function Team() {
  const [members, setMembers] = useState([]);
  const [loading, setLoading] = useState(true);
  const c = usePageContent('team');

  useEffect(() => {
    teamService.publicTeam().then(setMembers).catch(() => setMembers([])).finally(() => setLoading(false));
  }, []);

  return (
    <div className="container-page py-12 md:py-16">
      <BackLink className="mb-5" />
      <PageGuide
        id="team"
        className="mb-6"
        title="The people behind Rank Africa"
        steps={[
          'This page lists the team running the platform and reviewing student submissions.',
          'For partnerships, media or recruiter access, use the Contact page.',
        ]}
      />
      <EditableSection page="team" id="header" title="Header">
        <motion.div initial={{ opacity: 0, y: 6 }} animate={{ opacity: 1, y: 0 }} className="max-w-2xl">
          <p className="text-xs uppercase tracking-[0.2em] text-gold-400">{c.header.eyebrow}</p>
          <h1 className="font-display text-3xl sm:text-4xl font-extrabold mt-2">{c.header.heading}</h1>
          <p className="text-cream/60 mt-3">{c.header.subtitle}</p>
        </motion.div>
      </EditableSection>

      {loading ? (
        <div className="mt-10"><Loader /></div>
      ) : members.length === 0 ? (
        <p className="text-cream/50 mt-10">{c.header.emptyNote}</p>
      ) : (
        <div className="mt-10 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
          {members.map((m, i) => (
            <motion.div
              key={`${m.name}-${i}`}
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: Math.min(i * 0.05, 0.4) }}
              className="card p-6 text-center"
            >
              <div className="w-20 h-20 mx-auto rounded-full overflow-hidden bg-gold-400/15 grid place-content-center text-xl font-bold text-gold-300">
                {m.avatar_url ? (
                  <img src={m.avatar_url} alt={m.name} className="w-full h-full object-cover" />
                ) : (
                  initials(m.name)
                )}
              </div>
              <h3 className="font-semibold text-white mt-4">{m.name}</h3>
              {m.title && <p className="text-sm text-gold-300 mt-0.5">{m.title}</p>}
            </motion.div>
          ))}
        </div>
      )}
    </div>
  );
}
