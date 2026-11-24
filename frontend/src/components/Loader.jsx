import { Loader2 } from 'lucide-react';

export function Loader({ label }) {
  return (
    <div className="flex flex-col items-center justify-center gap-3 py-12 text-white/60">
      <Loader2 className="w-6 h-6 animate-spin text-gold-400" />
      {label && <span className="text-sm">{label}</span>}
    </div>
  );
}
