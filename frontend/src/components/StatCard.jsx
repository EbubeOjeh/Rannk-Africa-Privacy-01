import { motion } from 'framer-motion';

export function StatCard({ icon: Icon, label, title, sub, index = 0, accent }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.06 }}
      className="card p-5"
    >
      {(Icon || label) && (
        <div className="flex items-center gap-2 text-xs uppercase tracking-wider text-white/50">
          {Icon && (
            <span className="w-7 h-7 rounded-md bg-white/5 grid place-content-center">
              <Icon className="w-4 h-4 text-gold-400" />
            </span>
          )}
          {label}
        </div>
      )}
      <div className={`mt-3 font-display text-2xl font-bold ${accent || 'text-white'}`}>
        {title}
      </div>
      {sub && <div className="text-xs text-white/50 mt-1">{sub}</div>}
    </motion.div>
  );
}
