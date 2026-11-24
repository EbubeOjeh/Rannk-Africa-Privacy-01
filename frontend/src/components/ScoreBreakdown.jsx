import { motion } from 'framer-motion';
import { GraduationCap, FlaskConical, Award, Music, Sparkles } from 'lucide-react';
import { fmtScore } from '@/utils/format';

// Per-field score model: Technology/Music use Academic 40 + Project 40 +
// Achievements 20; every other field uses Academic 40 + Profile Assessment 60.
function pipelinesFor(student) {
  const slug = student.field_slug;
  const isProjectModel = !slug || slug === 'technology' || slug === 'music';
  if (isProjectModel) {
    const isMusic = slug === 'music';
    return [
      { key: 'academic_score', label: 'Academic', max: 40, icon: GraduationCap, blurb: 'WES-style 4.0 GPA equivalent' },
      {
        key: 'project_score',
        label: isMusic ? 'Portfolio' : 'Project',
        max: 40,
        icon: isMusic ? Music : FlaskConical,
        blurb: isMusic ? 'AI music-portfolio rubric' : 'AI rubric: 4 categories',
      },
      { key: 'achievement_score', label: 'Achievements', max: 20, icon: Award, blurb: 'Verified achievements' },
    ];
  }
  return [
    { key: 'academic_score', label: 'Academic', max: 40, icon: GraduationCap, blurb: 'WES-style 4.0 GPA equivalent' },
    {
      key: 'profile_score',
      label: 'Achievements & Profile',
      max: 60,
      icon: Sparkles,
      blurb: 'AI assessment of your accomplishments',
    },
  ];
}

export function ScoreBreakdown({ student, project, achievements = [] }) {
  const final = student.final_score ?? student.standardized_score ?? 0;
  const pipelines = pipelinesFor(student);
  const isProjectModel = pipelines.length === 3;
  const colors = ['bg-gold-400', 'bg-forest-400', 'bg-emerald-400'];

  return (
    <div className="card p-6">
      <div className="flex items-baseline justify-between">
        <div>
          <p className="text-xs uppercase tracking-wider text-cream/50">Final score</p>
          <h2 className="font-display text-3xl font-extrabold mt-1">
            {fmtScore(final)}
            <span className="text-cream/40 text-base font-semibold"> / 100</span>
          </h2>
        </div>
        <p className="text-xs text-cream/50 max-w-[14rem] text-right">
          {isProjectModel
            ? 'Academic /40 + Project /40 + Achievements /20.'
            : 'Academic /40 + Achievements & Profile Assessment /60.'}
        </p>
      </div>

      <div className="mt-5 h-2 bg-cream/5 rounded-full overflow-hidden flex">
        {pipelines.map((p, i) => {
          const value = student[p.key] ?? 0;
          const pct = (value / 100) * 100;
          return (
            <motion.span
              key={p.key}
              initial={{ width: 0 }}
              animate={{ width: `${pct}%` }}
              transition={{ duration: 0.5, delay: i * 0.1 }}
              className={`${colors[i]} h-full`}
              title={`${p.label}: ${fmtScore(value)} / ${p.max}`}
            />
          );
        })}
      </div>

      {(student.class_of_degree || student.standardized_gpa_4 != null) && (
        <div className="mt-5 rounded-xl bg-gold-400/[0.06] border border-gold-400/15 px-4 py-3 flex flex-wrap items-center gap-x-6 gap-y-2 text-sm">
          <span className="text-cream/60 text-xs uppercase tracking-wider">
            WES-style equivalency
          </span>
          {student.class_of_degree && (
            <span>
              <span className="text-cream/50">Class of degree:</span>{' '}
              <span className="font-semibold text-gold-300">{student.class_of_degree}</span>
            </span>
          )}
          {student.standardized_gpa_4 != null && (
            <span>
              <span className="text-cream/50">US 4.0 GPA:</span>{' '}
              <span className="font-semibold text-white tabular-nums">
                {fmtScore(student.standardized_gpa_4, 2)} / 4.00
              </span>
            </span>
          )}
          {student.raw_cgpa != null && (
            <span className="text-cream/50 text-xs">
              from {fmtScore(student.raw_cgpa, 2)} / {student.gpa_scale ?? 5}
            </span>
          )}
        </div>
      )}

      <div className={`mt-6 grid gap-3 ${isProjectModel ? 'sm:grid-cols-3' : 'sm:grid-cols-2'}`}>
        {pipelines.map((p) => {
          const value = student[p.key] ?? 0;
          const Icon = p.icon;
          return (
            <div key={p.key} className="bg-cream/5 rounded-xl p-4">
              <div className="flex items-center gap-2 text-[11px] uppercase tracking-wider text-cream/60">
                <Icon className="w-3.5 h-3.5 text-gold-400" /> {p.label}
              </div>
              <div className="font-display text-xl font-extrabold mt-2">
                {fmtScore(value)}
                <span className="text-cream/40 text-xs font-semibold"> / {p.max}</span>
              </div>
              <p className="text-[11px] text-cream/40 mt-1">{p.blurb}</p>
            </div>
          );
        })}
      </div>

      {isProjectModel && project && project.status !== 'pending' && (
        <div className="mt-6 border-t border-cream/10 pt-5">
          <p className="text-xs uppercase tracking-wider text-cream/50">
            {student.field_slug === 'music' ? 'Portfolio rubric breakdown' : 'Project rubric breakdown'}
          </p>
          <div className="mt-3 grid grid-cols-2 sm:grid-cols-4 gap-3">
            <RubricCell label={student.field_slug === 'music' ? 'Originality' : 'Originality'} value={project.originality} />
            <RubricCell label={student.field_slug === 'music' ? 'Production' : 'Technical Depth'} value={project.technical_depth} />
            <RubricCell label={student.field_slug === 'music' ? 'Reach' : 'Problem Solving'} value={project.problem_solving} />
            <RubricCell label={student.field_slug === 'music' ? 'Impact' : 'Innovation'} value={project.innovation} />
          </div>
        </div>
      )}

      {isProjectModel &&
        achievements.filter((a) => a.verification_status === 'verified').length > 0 && (
          <div className="mt-6 border-t border-cream/10 pt-5">
            <p className="text-xs uppercase tracking-wider text-cream/50">Verified achievements</p>
            <ul className="mt-2 text-sm text-cream/80 space-y-1">
              {achievements
                .filter((a) => a.verification_status === 'verified')
                .map((a) => (
                  <li key={a.id} className="flex justify-between">
                    <span>{a.title}</span>
                    <span className="text-gold-400 font-semibold">+{a.points} pts</span>
                  </li>
                ))}
            </ul>
          </div>
        )}
    </div>
  );
}

function RubricCell({ label, value }) {
  return (
    <div className="bg-cream/5 rounded-lg p-3">
      <div className="text-[10px] uppercase tracking-wider text-cream/50">{label}</div>
      <div className="font-bold mt-1">
        {fmtScore(value, 0)}
        <span className="text-cream/40 text-xs font-semibold"> / 10</span>
      </div>
    </div>
  );
}
