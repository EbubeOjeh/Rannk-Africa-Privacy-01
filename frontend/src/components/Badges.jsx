import clsx from 'clsx';

/**
 * A small, reusable row of badge chips.
 *
 * Renders nothing when there are no badges, so callers can drop it in without
 * guarding. Each badge is `{ badge_key?, label, emoji?, is_auto? }`.
 */
export function Badges({ badges = [], className }) {
  const list = Array.isArray(badges) ? badges.filter(Boolean) : [];
  if (list.length === 0) return null;

  return (
    <div className={clsx('flex flex-wrap gap-2', className)}>
      {list.map((b, i) => (
        <span
          key={b.badge_key || b.label || i}
          title={b.label}
          className="inline-flex items-center gap-1.5 rounded-full border border-gold-400/25 bg-gold-400/[0.08] px-2.5 py-1 text-xs font-semibold text-gold-200"
        >
          {b.emoji && <span aria-hidden="true">{b.emoji}</span>}
          <span>{b.label}</span>
        </span>
      ))}
    </div>
  );
}
