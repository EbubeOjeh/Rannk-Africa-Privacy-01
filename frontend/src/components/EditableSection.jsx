import { useEditContext } from '@/content/EditContext';

/**
 * Wraps a page section.
 *  - On the live public site: renders children with only the caller's own
 *    `className` (so a section that IS a styled card keeps its card styling,
 *    and a plain section adds no extra DOM). Zero visual change.
 *  - In the Website editor preview: adds a hover outline and, on click, opens
 *    that section's fields in the editor form (click-to-edit).
 */
export function EditableSection({ page, id, title, children, className = '' }) {
  const edit = useEditContext();

  if (!edit || edit.page !== page) {
    return className ? <div className={className}>{children}</div> : <>{children}</>;
  }

  const active = edit.activeSection === id;
  return (
    <div
      // Capture the click so inner links/buttons don't navigate or fire in the
      // preview — clicking anywhere in the section just opens its fields.
      onClickCapture={(e) => {
        e.preventDefault();
        e.stopPropagation();
        edit.onFocus?.(id);
      }}
      title={title ? `Edit: ${title}` : 'Edit this section'}
      className={`relative cursor-pointer rounded-lg transition ${
        active
          ? 'ring-2 ring-gold-400 ring-offset-2 ring-offset-ink-950'
          : 'ring-1 ring-transparent hover:ring-gold-400/50'
      } ${className}`}
    >
      {children}
    </div>
  );
}
