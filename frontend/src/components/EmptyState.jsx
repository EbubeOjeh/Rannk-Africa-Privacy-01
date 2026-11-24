import { Inbox } from 'lucide-react';

export function EmptyState({ title = 'Nothing here yet', description, icon: Icon = Inbox, action }) {
  return (
    <div className="flex flex-col items-center justify-center text-center py-16 px-4">
      <div className="w-12 h-12 rounded-xl bg-white/5 border border-white/5 flex items-center justify-center mb-3">
        <Icon className="w-5 h-5 text-white/50" />
      </div>
      <h3 className="text-white font-semibold">{title}</h3>
      {description && <p className="text-sm text-white/50 mt-1 max-w-sm">{description}</p>}
      {action && <div className="mt-4">{action}</div>}
    </div>
  );
}
