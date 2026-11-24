import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { UniversityCard } from '@/components/UniversityCard';
import { Loader } from '@/components/Loader';
import { EmptyState } from '@/components/EmptyState';
import { RankingsLocked } from '@/components/RankingsLocked';
import { EditableSection } from '@/components/EditableSection';
import { BackLink } from '@/components/BackLink';
import { PageGuide } from '@/components/PageGuide';
import { universitiesService } from '@/services/universities.service';
import { useRankingsRelease } from '@/hooks/useRankingsRelease';
import { usePageContent } from '@/hooks/usePageContent';

export default function Universities() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const release = useRankingsRelease();
  const c = usePageContent('universities');

  useEffect(() => {
    universitiesService
      .list({ page_size: 60 })
      .then((data) => setItems(data.items || []))
      .catch(() => setItems([]))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="container-page py-12">
      <BackLink className="mb-5" />
      <PageGuide
        id="universities"
        className="mb-6"
        title="Universities ranked by their students' results"
        steps={[
          'Each school is scored from the standardised results of its ranked students, so a small strong department is not buried by a large one.',
          'Tap a university to see its top-ranked students and the fields it performs best in.',
          'A school only appears once at least one of its students has been approved onto the leaderboard.',
        ]}
      />
      <EditableSection page="universities" id="header" title="Header">
        <motion.div initial={{ opacity: 0, y: 6 }} animate={{ opacity: 1, y: 0 }}>
          <p className="text-xs uppercase tracking-wider text-white/40">{c.header.eyebrow}</p>
          <h1 className="font-display text-3xl sm:text-4xl font-extrabold mt-1">{c.header.heading}</h1>
          <p className="text-sm text-white/50 mt-2 max-w-xl">{c.header.subtitle}</p>
        </motion.div>
      </EditableSection>

      {release.loading || loading ? (
        <Loader label="Loading universities…" />
      ) : !release.released ? (
        <RankingsLocked message={release.message} />
      ) : items.length === 0 ? (
        <EmptyState title="No universities registered yet" />
      ) : (
        <div className="mt-8 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {items.map((u, i) => (
            <UniversityCard key={u.id} uni={u} rank={i + 1} index={i} />
          ))}
        </div>
      )}
    </div>
  );
}
