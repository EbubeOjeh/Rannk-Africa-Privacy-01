import AuthorizedImage from './AuthorizedImage';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Bookmark, BookmarkCheck, Trophy, Lock } from 'lucide-react';
import { FieldChip } from './FieldChip';
import { ContactLinks } from './ContactLinks';
import { fmtScore, fmtRank } from '@/utils/format';

/**
 * Candidate card used across the employer Search and Saved pages.
 *
 * Props:
 *  - student:       a search/saved Card (see employer API contract).
 *  - onToggleSave:  (student) => void  — Save/Unsave handler.
 *  - busy:          disables the save button while a mutation is in flight.
 *  - approved:      whether the employer is approved (gates the contact note).
 *  - index:         for the staggered entrance animation.
 */
export function StudentResultCard({ student, onToggleSave, busy = false, approved = true, index = 0 }) {
  const saved = Boolean(student.saved);
  const skills = Array.isArray(student.skills) ? student.skills : [];
  const initials = (student.full_name || '?')
    .split(' ')
    .map((p) => p[0])
    .slice(0, 2)
    .join('')
    .toUpperCase();

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: Math.min(index * 0.04, 0.4) }}
      className="card p-5 flex flex-col gap-4"
    >
      <div className="flex items-start gap-3">
        {student.avatar_url ? (
          <AuthorizedImage
            src={student.avatar_url}
            alt={student.full_name}
            className="w-12 h-12 rounded-xl object-cover shrink-0"
          />
        ) : (
          <span className="w-12 h-12 rounded-xl bg-gold-400/15 grid place-content-center text-gold-300 font-semibold shrink-0">
            {initials}
          </span>
        )}
        <div className="min-w-0 flex-1">
          <Link
            to={`/students/${student.id}`}
            className="block font-semibold text-white hover:text-gold-400 truncate"
          >
            {student.full_name}
          </Link>
          <div className="text-xs text-cream/60 truncate">{student.university_name}</div>
          <div className="text-[11px] text-cream/40 truncate">
            {[student.course, student.academic_level, student.year_of_study && `Year ${student.year_of_study}`]
              .filter(Boolean)
              .join(' · ')}
          </div>
        </div>
        {onToggleSave && (
          <button
            onClick={() => onToggleSave(student)}
            disabled={busy}
            className={`btn-ghost text-xs shrink-0 ${saved ? 'text-gold-300' : ''}`}
            title={saved ? 'Remove from saved' : 'Save candidate'}
          >
            {saved ? <BookmarkCheck className="w-3.5 h-3.5" /> : <Bookmark className="w-3.5 h-3.5" />}
            {saved ? 'Saved' : 'Save'}
          </button>
        )}
      </div>

      <div className="flex flex-wrap items-center gap-2">
        {student.field_name && <FieldChip name={student.field_name} slug={student.field_name} />}
        <span className="pill bg-cream/10 text-cream/70">
          <Trophy className="w-3 h-3 text-gold-400" /> {fmtScore(student.final_score)} /100
        </span>
        {student.overall_rank != null && (
          <span className="text-[11px] text-cream/50">{fmtRank(student.overall_rank)} overall</span>
        )}
        {student.standardized_gpa_4 != null && (
          <span className="text-[11px] text-cream/40">
            WES {Number(student.standardized_gpa_4).toFixed(2)}/4.0
          </span>
        )}
      </div>

      {skills.length > 0 && (
        <div className="flex flex-wrap gap-1.5">
          {skills.slice(0, 8).map((s) => (
            <span key={s} className="tag bg-cream/5 text-cream/70">
              {s}
            </span>
          ))}
        </div>
      )}

      <div className="pt-1 border-t border-cream/5">
        {student.contact_unlocked ? (
          <ContactLinks
            email={student.email}
            whatsapp_number={student.whatsapp_number}
            linkedin_url={student.linkedin_url}
          />
        ) : (
          <div className="flex items-center gap-1.5 text-[11px] text-cream/40">
            <Lock className="w-3 h-3" />
            {'Contact details are excluded from discovery'}
          </div>
        )}
      </div>
    </motion.div>
  );
}
