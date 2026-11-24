# RankAfrica — Frontend

React + Vite + TailwindCSS frontend for the RankAfrica platform.

## Stack

- **React 18** + **Vite 5**
- **TailwindCSS 3** (custom dark theme, gold accent)
- **React Router v6** — routing
- **Axios** — HTTP client with JWT refresh
- **Zustand** — auth store, persisted to localStorage
- **Framer Motion** — page + list animations
- **Lucide Icons** — icon set
- **React Hot Toast** — notifications

## Quick start

```bash
cd frontend
cp .env.example .env       # adjust VITE_API_BASE_URL if needed
npm install
npm run dev
```

Open <http://localhost:5173>. The dev server proxies `/api` → `http://localhost:8000`.

## Folder structure

```
frontend/src/
├── assets/
├── components/        # reusable UI atoms / molecules
├── hooks/             # useAuth, useDebounce
├── layouts/           # PublicLayout, AdminLayout
├── pages/             # route components
│   └── admin/         # gated dashboard pages
├── routes/            # route definitions
├── services/          # api.js + per-resource service modules
├── store/             # zustand stores
├── styles/            # globals.css with Tailwind layers
├── utils/             # constants + format helpers
├── App.jsx
└── main.jsx
```

## Pages

Public:

- `/` — Home
- `/rankings` — Student rankings
- `/universities` — University leaderboard
- `/universities/:slug` — University profile
- `/fields` and `/fields/:slug` — Discipline rankings
- `/students/:id` — Student profile
- `/about` — About the engine
- `/login`, `/signup`

Admin (protected):

- `/admin` — Overview
- `/admin/upload` — Bulk transcript upload
- `/admin/students` — Manage students
- `/admin/scores` — Evaluated scores
- `/admin/analytics`
- `/admin/departments` — Department/field rankings
- `/admin/history`
- `/admin/settings`

## Theme

Defined in `tailwind.config.js`. Key tokens:

- `ink-*` — dark surface scale
- `gold-*` — accent
- `font-display` — Plus Jakarta Sans, used for headlines
- `font-sans` — Inter, used for body
