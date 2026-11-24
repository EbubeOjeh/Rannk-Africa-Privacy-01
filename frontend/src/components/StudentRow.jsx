import AuthorizedImage from './AuthorizedImage';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { RankBadge } from './RankBadge';
import { FieldChip } from './FieldChip';
import { fmtScore } from '@/utils/format';

/**
 * One leaderboard row, in two shapes.
 *
 * The 12-column `data-row` carries a 44rem min-width (globals.css) and scrolls
 * sideways inside its wrapper — which put the score ~300px off-screen on a
 * phone, so a mobile visitor saw the rank numbers but never the scores they
 * explain. Below `sm` we therefore render a compact card that keeps rank, name
 * and score on one line; the wide grid takes over from `sm` up.
 */
export function StudentRow({ student, index = 0 }) {
  const score = student.final_score ?? student.standardized_score;
  const rank = student.overall_rank ?? index + 1;

  return (
    <motion.div
      initial={{ opacity: 0, y: 6 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: Math.min(index * 0.02, 0.4) }}
    >
      {/* ── Mobile card ── */}
      <Link
        to={`/students/${student.id}`}
        className="sm:hidden flex items-center gap-3 px-4 py-3 border-b border-cream/5 active:bg-cream/[0.04]"
      >
        <RankBadge rank={rank} />
        {student.avatar_url && <AuthorizedImage src={student.avatar_url} alt="Shared profile photo" className="w-10 h-10 rounded-full object-cover shrink-0" />}
        <div className="min-w-0 flex-1">
          <div className="text-sm font-medium text-white truncate">{student.full_name}</div>
          <div className="text-[11px] text-cream/50 truncate">
            {student.university_name}
            {student.field_name && ` · ${student.field_name}`}
          </div>
        </div>
        <div className="text-sm font-semibold text-white tabular-nums whitespace-nowrap shrink-0">
          {fmtScore(score)}
          <span className="text-cream/40 text-xs"> /100</span>
        </div>
      </Link>

      {/* ── Desktop / tablet row ── */}
      <div className="data-row hidden sm:grid">
        {/* Rank */}
        <div className="col-span-1">
          <RankBadge rank={rank} />
        </div>

        {/* Name. The degree class and WES 4.0 equivalent used to sit under it;
            they are deliberately not shown on the leaderboard any more. Both
            remain on the student's own profile, where the full score
            breakdown gives them context. */}
        <div className="col-span-4 flex items-center gap-3 min-w-0">
          {student.avatar_url && <AuthorizedImage src={student.avatar_url} alt="Shared profile photo" className="w-10 h-10 rounded-full object-cover shrink-0" />}
          <Link
            to={`/students/${student.id}`}
            className="block text-sm font-medium text-white hover:text-gold-400 truncate"
          >
            {student.full_name}
          </Link>
        </div>

        {/* School · State */}
        <div className="col-span-4">
          <div className="text-sm text-cream/80 truncate">{student.university_name}</div>
          {student.university_state && (
            <div className="text-[10px] text-cream/50 mt-0.5 truncate">
              {student.university_state}
            </div>
          )}
        </div>

        {/* Discipline */}
        <div className="col-span-2 truncate">
          {student.field_name && <FieldChip name={student.field_name} slug={student.field_name} />}
        </div>

        {/* Score */}
        <div className="col-span-1 text-right text-sm font-semibold text-white tabular-nums whitespace-nowrap">
          {fmtScore(score)}
          <span className="text-cream/40 text-xs"> /100</span>
        </div>
      </div>
      <div className="px-4 sm:px-6 pb-3">
  <Link
    to={`/students/${student.id}`}
    className="btn-ghost text-sm"
  >
    View Profile
  </Link>
</div>
      {(student.bio || student.portfolio_url) && <div className="px-4 sm:px-6 pb-3 space-y-2 text-sm">
        {student.bio && <p className="text-cream/70 whitespace-pre-wrap break-words">{student.bio}</p>}
        {student.portfolio_url && /^https?:\/\//i.test(student.portfolio_url) && <a href={student.portfolio_url} target="_blank" rel="noopener noreferrer" className="text-gold-300 underline break-all">View portfolio</a>}
      </div>}
    </motion.div>
  );
}
