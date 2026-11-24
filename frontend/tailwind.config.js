/** @type {import('tailwindcss').Config} */
// Palette mapped to the RankAfrica spec:
//   Primary  — Dark Green   #1A3D2B (lives in the ink scale, mid-tones)
//   Accent   — Copper/Gold  #C47C2B (gold-400 in the legacy class names)
//   Surface  — Cream / Off  #F9F5EE (cream)
//   Text     — Near Black   #1A1A1A (ink-text)
//
// Existing components use class names like `bg-ink-950`, `bg-gold-400`,
// `border-white/5` — so we re-mapped the underlying hex values rather than
// renaming every class. The result honors the spec without a sweeping rewrite.
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        ink: {
          // Near-black neutral surface palette to match the prototype
          // (950 = darkest page bg, ascending = cards/raised surfaces).
          950: '#0a0a0b',
          900: '#101012',
          850: '#161618',
          800: '#1d1d20',
          700: '#27272b',
          600: '#34343a',
          text: '#111111', // dark text used on gold buttons
        },
        gold: {
          50:  '#fdf6e6',
          100: '#f8e6b8',
          200: '#f0d184',
          300: '#ecc15a', // hover
          400: '#E2A828', // spec ACCENT — amber/gold (prototype)
          500: '#c28f22',
          600: '#9c711b',
          700: '#735315',
        },
        forest: {
          50:  '#eaf3ed',
          100: '#c8dfd0',
          200: '#9abfa9',
          300: '#6ba082',
          400: '#3f8262',
          500: '#236547',
          600: '#1A3D2B', // = primary
          700: '#143020',
          800: '#0e2418',
          900: '#061b10',
        },
        cream: {
          DEFAULT: '#F9F5EE',
          50:  '#fdfaf3',
          100: '#F9F5EE',
          200: '#efe6d2',
          300: '#e1d3b3',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        display: ['"Plus Jakarta Sans"', 'Inter', 'sans-serif'],
      },
      boxShadow: {
        glow: '0 0 0 1px rgba(226, 168, 40, 0.22), 0 10px 40px -12px rgba(226, 168, 40, 0.30)',
        card: '0 1px 0 rgba(255,255,255,0.04) inset, 0 12px 32px -16px rgba(0,0,0,0.85)',
      },
      backgroundImage: {
        // Subtle warm "network" glow on near-black (kept restrained per brief).
        'hero-grid':
          "radial-gradient(circle at 75% 25%, rgba(226,168,40,0.10), transparent 55%), radial-gradient(circle at 10% 0%, rgba(226,168,40,0.05), transparent 45%)",
      },
      animation: {
        'fade-up': 'fadeUp 0.6s ease-out both',
        shimmer: 'shimmer 2.4s linear infinite',
      },
      keyframes: {
        fadeUp: { '0%': { opacity: 0, transform: 'translateY(12px)' }, '100%': { opacity: 1, transform: 'translateY(0)' } },
        shimmer: { '0%': { backgroundPosition: '-200% 0' }, '100%': { backgroundPosition: '200% 0' } },
      },
    },
  },
  plugins: [],
};
