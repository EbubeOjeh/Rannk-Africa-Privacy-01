import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { MapPin, ArrowRight } from 'lucide-react';
import { FieldChip } from './FieldChip';
import { fmtScore } from '@/utils/format';

export function UniversityCard({ uni, rank, index = 0 }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: Math.min(index * 0.04, 0.4) }}
      className="card p-5 hover:border-gold-400/30 transition-colors"
    >
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-center gap-3 min-w-0">
          <div className="shrink-0 w-9 h-8 rounded-md bg-white/5 grid place-content-center text-sm font-bold text-white/80">
            {rank ?? uni.overall_rank ?? '—'}
          </div>
          <div className="min-w-0">
            <Link to={`/universities/${uni.slug}`} className="block">
              <h3 className="font-semibold text-white truncate hover:text-gold-400">
                {uni.name}
              </h3>
            </Link>
            {uni.city && (
              <div className="flex items-center gap-1 text-xs text-white/40 mt-0.5">
                <MapPin className="w-3 h-3" /> {uni.city}
              </div>
            )}
          </div>
        </div>
        <span className="tag bg-white/5 border border-white/10 text-gold-300 text-[10px]">
          Tier {uni.tier ?? 3}
        </span>
      </div>

      <div className="grid grid-cols-3 gap-3 mt-5">
        <Stat label="Avg Score" value={`${fmtScore(uni.avg_score)}`} />
        <Stat label="Students" value={uni.student_count ?? 0} />
        <Stat label="Top Score" value={fmtScore(uni.top_score)} />
      </div>

      {uni.field_tags?.length > 0 && (
        <div className="flex flex-wrap gap-1.5 mt-4">
          {uni.field_tags.slice(0, 5).map((t) => (
            <FieldChip key={t} name={t} slug={t} />
          ))}
        </div>
      )}

      <Link
        to={`/universities/${uni.slug}`}
        className="mt-5 inline-flex items-center gap-1 text-sm text-gold-400 hover:text-gold-300"
      >
        View Students <ArrowRight className="w-3.5 h-3.5" />
      </Link>
    </motion.div>
  );
}

function Stat({ label, value }) {
  return (
    <div>
      <div className="text-lg font-bold text-white tabular-nums">{value}</div>
      <div className="text-[11px] uppercase tracking-wider text-white/40">{label}</div>
    </div>
  );
}
