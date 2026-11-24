import { Link } from 'react-router-dom';

/**
 * RankAfrica brand mark.
 *
 * Inline SVG (no asset to ship). Layout matches the banner from the brand
 * deck — graduation cap + open-book podium on a dark green plaque, with the
 * dual-tone "RANK AFRICA" wordmark and the "Ranking Student Excellence"
 * tagline. ``size`` controls the overall density so the mark looks right in
 * a 64px navbar slot and in a hero hero badge alike.
 */
export function Logo({ to = '/', size = 'md' }) {
  const sizes = {
    sm: { plaque: 'w-7 h-7',  title: 'text-base', tagline: 'text-[7px]', gap: 'gap-2'   },
    md: { plaque: 'w-9 h-9',  title: 'text-lg',   tagline: 'text-[8px]', gap: 'gap-2.5' },
    lg: { plaque: 'w-12 h-12', title: 'text-2xl', tagline: 'text-[10px]', gap: 'gap-3'  },
  };
  const s = sizes[size] || sizes.md;

  return (
    <Link to={to} className={`flex items-center ${s.gap} group select-none`}>
      <span className={`${s.plaque} shrink-0 rounded-lg bg-white grid place-content-center overflow-hidden`}>
        <BrandMark />
      </span>

      <div className="flex flex-col leading-none">
        <div className={`font-display font-extrabold tracking-tight ${s.title}`}>
          <span className="text-white">RANK</span>
          <span className="text-gold-400">AFRICA</span>
        </div>
        <div className={`uppercase ${s.tagline} tracking-[0.25em] text-cream/60 mt-1`}>
          Ranking Student Excellence
        </div>
      </div>
    </Link>
  );
}

/** Official RankAfrica brand mark (the RA monogram in public/ranklogo.png).
 *  Used by Logo and anywhere needing the symbol without the wordmark. */
export function BrandMark({ className = 'w-full h-full' }) {
  return (
    <img
      src="/ranklogo.png"
      alt="RankAfrica"
      className={`${className} object-contain`}
      draggable={false}
    />
  );
}
