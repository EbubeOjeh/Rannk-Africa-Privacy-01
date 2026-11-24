import clsx from 'clsx';

export function RankBadge({ rank }) {
  if (!rank) return <span className="text-white/30">—</span>;
  const top = rank <= 3;
  const palette =
    rank === 1
      ? 'bg-gold-400 text-ink-950'
      : rank === 2
      ? 'bg-zinc-200 text-ink-950'
      : rank === 3
      ? 'bg-amber-700 text-white'
      : 'bg-white/5 text-white/70';
  return (
    <span
      className={clsx(
        'inline-flex items-center justify-center w-8 h-7 rounded-md text-xs font-bold',
        palette,
        top && 'shadow-glow'
      )}
    >
      {rank}
    </span>
  );
}
