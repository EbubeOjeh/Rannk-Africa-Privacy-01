# RankAfrica — PRS v2.0 Gap Analysis & Build Roadmap

> **Status:** Planning document — no code has been changed.
> **Date:** 2026-06-27 · **Doc version:** 1.0
> **Source spec:** *Rank Africa Product Requirements Specification (PRS) Version 2.0 — Student Recognition & Opportunity Platform.*
> **Audience:** Offia Studio engineering + the RankAfrica client.
>
> This document compares the **code as it exists today** against **PRS v2.0**, then lays out a
> dependency-ordered roadmap to close the gap. It is the single source of truth for "where are we vs.
> where the spec wants us" until v2.0 ships.

---

## 0. Two decisions locked in before reading

1. **Registration model = HYBRID.** The PRS says *"students register individually"* ([§4](#)). We will make
   **student self-registration the primary entry point**, but **keep the existing school-admin tooling as an
   optional verification + bulk-upload layer**. Schools become *verifiers of their own students*, not the only
   door in. This preserves the substantial admin investment already built (transcript ingestion, approval
   queues, cycles) instead of discarding it.

2. **Keep the current stack.** PRS §20 recommends Next.js / Node-Express / MongoDB. The actual project is
   **React + Vite / FastAPI / SQLAlchemy / Postgres (Supabase)** with **Anthropic Claude** for AI. That stack
   is more capable than the §20 boilerplate and already implements most of the admin spec. **§20 is treated as
   a generic template, not a directive to rewrite.** (Same posture as the stale v1 README: trust the code.)

---

## 1. Executive summary

**This PRS is a pivot, not a patch.** Today's RankAfrica is a **university-centric, batch** platform: a *school
admin* registers an institution, gets approved, then uploads students/transcripts/projects/achievements.
Students are records, not users. PRS v2.0 describes a **student-centric, self-service** platform where students
register themselves and employers + admins orbit them. That one change cascades into the scoring engine, the
data model, the field taxonomy, and every dashboard.

Three structural shifts plus five net-new product surfaces:

| # | Shift | Today | PRS v2.0 | Size |
|---|-------|-------|----------|------|
| 1 | **Entry model** | School admin uploads students | Students self-register (hybrid: schools stay as verifiers) | 🔴 Large |
| 2 | **Scoring** | 3 components: Academic/40 + Project/40 + Achievements/20 | 6 components: Acad 40 + Research 15 + Projects 15 + Leadership 10 + Internships 10 + Competitions 10 | 🔴 Large |
| 3 | **Fields** | 5 tech-only fields | 8 broad disciplines + automatic course→field mapping | 🟠 Medium |
| 4 | **Opportunity portal** | Does not exist | Internships/jobs/scholarships/research/competitions + AI "% Match" | 🔴 Large |
| 5 | **AI integrity suite** | Project scoring only | + fraud / fake-transcript / plagiarism / duplicate detection → review queue | 🔴 Large |
| 6 | **Employer dashboard** | Register → browse rankings → 1-way relay message | Search/filter, save candidates, post opportunities, multi-channel contact | 🟠 Medium |
| 7 | **Verification badges** | None | Verified Student / Research / Internship / Music / Competition / Scholarship | 🟢 Small |
| 8 | **Homepage** | "Launching soon" placeholder | Hero + featured rankings + stats + opportunities + employer logos | 🟢 Small |

**Good news — already aligned:** the WES academic engine, the rankings UI (built, just hidden behind the launch
gate), submission-cycle locking, admin approval queues, analytics, team/permissions, and the no-code site
editor all map cleanly to the PRS admin section and survive the pivot largely intact.

---

## 2. Current architecture snapshot (so this doc stands alone)

- **Backend:** FastAPI (Python 3.11), SQLAlchemy 2, Pydantic v2, Alembic. SQLite dev / Supabase Postgres prod.
  Custom JWT (access + refresh) with a role + fine-grained permission catalog.
- **Frontend:** React 18 + Vite, Zustand (persisted auth), Axios (JWT-refresh interceptor).
- **AI:** Anthropic Claude (`claude-sonnet-4-6`), gated by `AI_ENABLED` + `ANTHROPIC_API_KEY`.
- **Roles today** (`backend/app/models/user.py:17`): `super_admin`, `school_admin`, `university_admin` (legacy
  alias), `student`, `employer`, `evaluator`, `employee`.
- **Signup paths today** (`backend/app/api/v1/endpoints/auth.py:32`): `register-school`, `register-recruiter`.
  **No student self-registration.**
- **Scoring today** (`backend/app/services/evaluation_engine/engine.py:3`):
  `final/100 = Academic/40 + Project/40 + Achievements/20`.
- **Public site** is intentionally a "launching soon" page; `/rankings`, `/universities`, `/fields`,
  `/students`, `/about`, `/team` redirect to `/`; sign-in is at `/platform` (`frontend/src/routes/index.jsx`).

---

## 3. Gap analysis by PRS domain

Legend: ✅ Exists · 🟡 Partial · ❌ Missing

### 3.1 User types & registration (PRS §3–§5)

| PRS requirement | Status | Notes / what's needed |
|---|---|---|
| **Student** self-registers, builds own profile | ❌ | No student signup endpoint or UI. Today students are admin-created records. **Core of the pivot.** |
| Automatic field assignment from chosen course | ❌ | `field_id` is set manually. Need a course→field mapping service (PRS §4 examples). |
| **Employer** registers, vetted, approved | 🟡 | `register-recruiter` + approval queue exist. Missing: employer *profile*, logo, dashboard. |
| **Administrator** oversight | ✅ | Super-admin dashboard, approvals, analytics, cycles, team/permissions all exist. |
| School-admin entry retained (hybrid) | ✅ | Keep `register-school`, transcript bulk upload, approval — repurpose schools as **verifiers**. |

### 3.2 Student profile & data model (PRS §5, §9)

| PRS data the student supplies | Status | Backing entity today |
|---|---|---|
| Personal (name, photo, university, faculty, dept, course, year) | 🟡 | `students` table has most; entered by admin, not student. |
| Academic — CGPA + most-recent-semester result | ✅ | `transcripts` + `transcript_courses`; WES standardization works. |
| **Projects** (final-year, software, design, portfolios, music, research…) | 🟡 | `project_submissions` — **but unique 1-per-student.** PRS implies *many*. Needs 1→N. |
| **Research & Publications** (journals, conf papers, chapters…) | ❌ | Only a flat `achievement` type `PUBLICATION=6pts`. Needs a real `research` entity. |
| **Experience** (internships, volunteer, startups, employment) | ❌ | Only `achievement` type `INTERNSHIP=3pts`. Needs an `experience` entity. |
| **Competitions** (hackathons, moot court, debate, music awards…) | ❌ | Only hackathon achievement types. Needs a `competitions` entity. |
| **Verified achievements** (awards, certs, scholarships, grants…) | 🟡 | `achievements` table + verification status exists; broaden types. |
| **Professional links** (LinkedIn, WhatsApp, portfolio, GitHub, Behance, Scholar, Spotify/YT) | ❌ | Only LinkedIn captured. Need a links sub-model (field-aware). |
| Bio, skills, languages, resume/CV | 🟡 | Bio exists; skills/languages/CV upload missing. |
| Public profile (photo, scores, ranks, badges, downloadable CV) | 🟡 | `StudentProfile.jsx` exists (redirected); no badges, no CV download. |

### 3.3 AI evaluation framework (PRS §6–§7) — the scoring rewrite

**Weight change** — the headline of the whole engine:

| Dimension | Today | PRS v2.0 | Reuse? |
|---|---|---|---|
| Academic Performance | /40 (WES) | **40%** | ✅ **Keep WES engine as-is** (`wes_equivalency.py`). |
| Research & Publications | inside Achievements/20 | **15%** | ❌ New scorer + data (count, quality, impact, citations). |
| Projects & Innovation | /40 (Claude, 4×/10 rubric) | **15%** | 🟡 Reuse Claude rubric — **re-scale 40 → 15**. |
| Leadership & Extracurricular | inside Achievements/20 | **10%** | ❌ New entity + scorer. |
| Internships & Experience | inside Achievements/20 | **10%** | ❌ New scorer (relevance, duration, org quality, responsibilities). |
| Competitions & Verified Achievements | inside Achievements/20 | **10%** | 🟡 Refactor achievements → weighted competition/award scorer. |

> **Key migration insight:** Academic survives untouched. The **Projects pipeline shrinks 40→15** (same Claude
> rubric, new scale). The flat **Achievements/20 fragments into four separately-modeled, separately-weighted
> dimensions** (Research 15, Leadership 10, Internships 10, Competitions 10 = 45 pts) — each needs richer input
> data than a single point value. Bump `ENGINE_VERSION` and run v2 and v2.1 side-by-side behind a flag so live
> scores don't break mid-migration.

**AI verification / fraud (PRS §7)** — all ❌ today (Claude only scores projects):

- Fake / edited transcript detection · edited-certificate detection · duplicate-publication detection ·
  plagiarized-project detection · suspicious-claim flagging · duplicate-account detection.
- All flagged items route to a **manual-review queue** before they affect rankings (new admin surface).

### 3.4 Rankings (PRS §8)

| Ranking | Status | Notes |
|---|---|---|
| Overall student ranking | ✅ | Exists (`Rankings.jsx`), gated behind launch redirect. |
| Field rankings (per discipline) | ✅ | Exists; depends on the 8-field migration landing first. |
| **University ranking per field** | 🟡 | Department/field rankings exist; per-field *university* ranking needs verifying. |
| **Overall university ranking** | ❌ | PRS §8 wants a specific anti-skew formula: avg student score + # top-ranked students + cross-discipline consistency + verified achievements, so *one star student can't dominate*. Needs design. |

### 3.5 Homepage (PRS §10)

`Home.jsx` already renders hero + 8 field cards + about/mission/vision + opportunity cards + contact, all
editable via the site editor — **but it's a "launching soon" placeholder** (cards open "coming soon" modals).
Missing live data: **featured rankings** (highest-rated student, top university, per-field top students),
**platform statistics** (registered students, universities, employers, opportunities, placements), **latest
opportunities** feed, **featured employer logos**.

### 3.6 Student dashboard (PRS §11) — ❌ mostly missing

Needs: overall AI score, national/university/field rank, **AI recommendations to improve profile**, missing-info
prompts, verification status, **matched opportunities**, employer messages, notifications. Only `notifications`
infrastructure exists today.

### 3.7 Employer dashboard, opportunities & messaging (PRS §12, §15, §16)

| PRS requirement | Status | Notes |
|---|---|---|
| Employer registration + approval gate | ✅ | Exists. |
| Search students | ✅ | Rankings UI has search/filter. |
| Filter (university, field, skills, GPA, grad year, AI score) | 🟡 | Some filters exist; skills/grad-year/score-range need adding. |
| **Save candidates** | ❌ | No `saved_candidates` entity. |
| **Post opportunities** | ❌ | No `opportunities` entity or UI. |
| **Opportunity portal** w/ AI "% Match" | ❌ | Net new: browse + per-student compatibility score. |
| Contact via WhatsApp / LinkedIn / Email | 🟡 | One-way relay (`ContactStudentForm`) exists. PRS wants multi-channel deep links — **reuse the `wa.me` pattern from offia-tech / Luamé**. |
| Featured employers (logos) | ❌ | New. |

### 3.8 Trust, security & terms (PRS §14, §17, §18)

- **Verification badges (§14)** — ❌ none. New `badges` + `student_badges` join + display.
- **T&C consent gate (§18)** — ❌ The exact confirmation copy must appear and be actively accepted *before*
  profile submission; record `terms_acceptances` (version + timestamp) for legal cover.
- **Security (§17)** — 🟡 JWT, hashed passwords, audit logs exist. Document validation, AI fraud detection,
  and a flagged-submission review path are missing (covered by §3.3).

---

## 4. Data model change summary

**New tables:** `research_publications`, `experiences`, `competitions`, `leadership_activities`,
`opportunities`, `saved_candidates`, `badges` + `student_badges`, `terms_acceptances`, `ai_flags` (review
queue), `employer_profiles` (extend the `employer` user with logo/website/about/approval metadata),
`opportunity_matches` (cached AI compatibility scores).

**Modified tables:** `students` (+ self-registration fields, skills, languages, resume_url, professional links,
`terms_accepted`); `project_submissions` (drop the **unique** 1-per-student constraint → allow many); `fields`
(seed the **8** disciplines, retire the 5 tech-only seeds) + a `course_field_map`; the **evaluation engine**
(`engine.py` + new per-dimension scorers, `ENGINE_VERSION` bump, feature flag).

---

## 5. Phased roadmap (dependency-ordered)

> Each phase is shippable. Push to `main` per workspace rules only after typecheck/build passes (frontend +
> backend Vercel projects). AI-heavy phases must account for Vercel's 10s function limit — see Risks.

### Phase 0 — Foundation (no user-visible change)
- Seed the **8 PRS fields**; build the **course→field mapping** service; migrate existing students onto them.
- Add the new sub-entities (research / experience / competitions / leadership) as first-class tables.
- Add `opportunities`, `saved_candidates`, `badges`, `terms_acceptances`, `ai_flags` schemas (empty).
- Implement the **6-component scoring engine** behind a flag (`ENGINE_VERSION='v2.1'`), running alongside v2.
- **Exit criteria:** migrations apply clean on Supabase; old scores reproducible under v2; new engine unit-tested.

### Phase 1 — Student self-service (the pivot core, hybrid)
- Student **self-registration** endpoint + UI; course auto-maps to field.
- **Profile builder** covering every PRS §5 section (personal, CGPA upload, projects [N], research, experience,
  competitions, achievements, links, bio/skills/languages/CV).
- **T&C consent gate** with the exact §18 copy; persist acceptance.
- **Student dashboard** (§11): score, ranks, verification status, missing-info prompts, notifications.
- Keep school-admin bulk upload; schools now **verify** their students (hybrid). Re-score under v2.1.
- **Exit criteria:** a student can self-register → build profile → see a live /100 score and rank.

### Phase 2 — Public launch surfaces
- Un-gate `/rankings`, `/students/:id`, field/university pages.
- **Overall + per-field university ranking** algorithm (anti-skew, §8).
- Full **homepage** (§10): featured rankings, platform stats, latest opportunities, employer logos.
- **Verification badges** display on profiles.
- **Exit criteria:** public visitor sees real rankings, real stats, real profiles with badges.

### Phase 3 — Employer & opportunities
- **Employer dashboard:** advanced filters, **save candidates**, **post opportunities**.
- **Opportunity portal** for students (browse internships/jobs/scholarships/research/competitions).
- **Multi-channel contact** (WhatsApp `wa.me` + LinkedIn + email deep links — reuse `src/lib/whatsapp.ts` pattern).
- Featured-employer management.
- **Exit criteria:** employer posts an opportunity; student browses it; employer saves + contacts a candidate.

### Phase 4 — AI integrity & matching
- **Fraud suite:** fake/edited transcript, edited certificate, plagiarism, duplicate-account,
  duplicate-publication detection → **manual-review queue** for admins.
- **AI opportunity matching** ("% Match") + **AI profile recommendations** for students.
- **Badge automation** (auto-award on verified evidence).
- **Exit criteria:** a forged upload gets flagged and held out of rankings; students see a match score.

### Phase 5 — PRS Phase-2 items (explicitly future, §19)
- AI CV builder, interview prep, scholarship recommender, career roadmaps, employability score, annual awards,
  university analytics, employer talent insights, mobile apps. *Out of v2.0 scope; parked here for visibility.*

---

## 6. Risks & still-open decisions

- **AI cost & latency on Vercel.** The fraud suite multiplies Claude calls; project scoring already risks
  Vercel Hobby's 10s limit. Decide: Vercel **Pro** vs. moving AI to **background jobs / a worker** (recommended
  for Phase 4). Keep `AI_ENABLED` graceful-degradation so the platform works with AI off.
- **Hybrid trust rules.** Define precisely what a *self-registered* student can claim vs. what requires
  **school verification** before it counts toward ranking (e.g. CGPA must be school- or transcript-verified).
- **"% Match" definition.** Agree the compatibility formula (skills overlap + field + score + grad year) before
  building §15.
- **WhatsApp contact.** Confirm it's free `wa.me` deep links (like offia-tech/Luamé), **not** the paid Business API.
- **Overall-university anti-skew formula (§8).** Needs sign-off before Phase 2.
- **Project 1→N + AI cost.** Allowing many projects per student multiplies scoring calls — cap or queue.

---

## 7. Appendix — load-bearing files

| Concern | File |
|---|---|
| Roles / users | `backend/app/models/user.py:17` |
| Permissions catalog | `backend/app/core/permissions.py:18` |
| Signup paths | `backend/app/api/v1/endpoints/auth.py:32` |
| Scoring orchestrator | `backend/app/services/evaluation_engine/engine.py:3` |
| Academic (WES) | `backend/app/services/evaluation_engine/wes_equivalency.py` |
| Project AI rubric | `backend/app/services/evaluation_engine/project_ai.py` |
| Achievement points | `backend/app/services/evaluation_engine/achievement.py:40` |
| Field seeds (5 tech) | `backend/app/db/seed.py:33` |
| API route map | `backend/app/api/v1/router.py` |
| Prod schema | `backend/supabase/schema.sql` |
| Frontend routes / launch gate | `frontend/src/routes/index.jsx` |
| Homepage | `frontend/src/pages/Home.jsx` |
| Rankings UI | `frontend/src/pages/Rankings.jsx` |
| Public student profile | `frontend/src/pages/StudentProfile.jsx` |
| Admin pages | `frontend/src/pages/admin/*` |
| One-way contact form | `frontend/src/components/ContactStudentForm.jsx` |

---

*End of document. No code was modified to produce this analysis.*
