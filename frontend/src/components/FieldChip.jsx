import clsx from 'clsx';
import { fieldStyle } from '@/utils/constants';

export function FieldChip({ name, slug, size = 'sm' }) {
  if (!name) return null;
  const style = fieldStyle(slug || name);
  return (
    <span
      className={clsx(
        'tag',
        style.bg,
        style.text,
        size === 'lg' ? 'px-3 py-1 text-xs' : 'px-2 py-0.5 text-[11px]'
      )}
    >
      {name}
    </span>
  );
}
