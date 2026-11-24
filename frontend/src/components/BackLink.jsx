import { useLocation, useNavigate } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';

/**
 * "Back" control for inner pages.
 *
 * Goes back through history when there is somewhere to go back to. React Router
 * labels the first entry of a session `default`, so a visitor who landed here
 * directly (typed URL, shared link, search result) has no previous page — they
 * get a link to `fallback` instead of a dead button that does nothing.
 */
export function BackLink({ fallback = '/', label = 'Back', className = '' }) {
  const navigate = useNavigate();
  const location = useLocation();
  const canGoBack = location.key !== 'default';

  return (
    <button
      type="button"
      onClick={() => (canGoBack ? navigate(-1) : navigate(fallback))}
      className={`inline-flex items-center gap-1.5 text-sm text-cream/60 hover:text-gold-300 transition-colors ${className}`}
    >
      <ArrowLeft className="w-4 h-4" />
      {canGoBack ? label : 'Back to home'}
    </button>
  );
}
