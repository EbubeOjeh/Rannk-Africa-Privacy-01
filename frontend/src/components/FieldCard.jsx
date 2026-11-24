import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  Stethoscope,
  Code2,
  Scale,
  Calculator,
  Wrench,
  ArrowRight,
  GraduationCap,
} from 'lucide-react';

const ICONS = {
  stethoscope: Stethoscope,
  code: Code2,
  scale: Scale,
  calculator: Calculator,
  wrench: Wrench,
};

export function FieldCard({ field, index = 0 }) {
  const Icon = ICONS[field.icon] || GraduationCap;
  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: Math.min(index * 0.04, 0.4) }}
    >
      <Link
        to={`/fields/${field.slug}`}
        className="card p-5 hover:border-gold-400/30 transition-colors group block h-full"
      >
        <div
          className="w-10 h-10 rounded-lg flex items-center justify-center mb-4"
          style={{ background: `${field.color || '#ffc740'}20` }}
        >
          <Icon className="w-5 h-5" style={{ color: field.color || '#ffc740' }} />
        </div>
        <h3 className="font-semibold text-white">{field.name}</h3>
        <p className="text-xs text-white/40 mt-1">View top students &amp; universities</p>
        <div className="mt-4 text-gold-400 inline-flex items-center gap-1 text-sm">
          <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
        </div>
      </Link>
    </motion.div>
  );
}
