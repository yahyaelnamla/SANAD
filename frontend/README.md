# SANAD Frontend

Next.js 14 application for the SANAD Shariah financial reasoning platform.

## Features

- **Multi-agent chat** — SSE streaming, execution trace, voice input/TTS, Fanar model selector
- **Explainability chain** — Evidence → Principles → Reasoning → Analysis
- **Scanners** — AAOIFI company and portfolio Shariah screening
- **Zakat calculator** — live prices + fiqh guidance
- **Documents** — PDF upload, OCR analysis, document Q&A
- **Scholars** — directory and profile pages
- **Knowledge base & graph** — source browser + Three.js visualization
- **Evaluation dashboard** — hackathon judge harness
- **Admin** — source CRUD and analytics (admin role)
- **Auth** — JWT login/register, Google/Microsoft SSO, onboarding wizard
- **i18n** — Arabic (RTL default) and English (LTR)
- **Themes** — light, night-blue, dark-gray, system
- **PWA** — service worker, install prompt, offline query queue

## Setup

```bash
cd frontend
cp .env.example .env.local
npm install
npm run dev
```

Open [http://localhost:3000/welcome](http://localhost:3000/welcome). Unauthenticated users are redirected to `/login` on protected routes.

## Environment variables

| Variable | Description |
|----------|-------------|
| `NEXT_PUBLIC_API_URL` | Backend API base URL. Empty string uses same-origin proxy via `next.config.mjs` (production). Dev default: `http://localhost:8000` |

## Scripts

| Command | Description |
|---------|-------------|
| `npm run dev` | Start development server |
| `npm run build` | Production build (standalone output) |
| `npm run test` | Run Vitest unit tests |
| `npm run lint` | ESLint |

## Stack

- Next.js 14 (App Router)
- React 18, TypeScript
- Tailwind CSS + Shadcn/Radix UI
- Zustand (auth, conversations, settings, bookmarks)
- Framer Motion, Three.js (knowledge graph)
- next-themes

## Routes

| Route | Guard | Purpose |
|-------|-------|---------|
| `/welcome` | Public | Marketing landing |
| `/login`, `/register` | Public | Authentication |
| `/onboarding` | Auth | User setup wizard |
| `/chat` | Auth | Main AI chat |
| `/history`, `/history/[queryId]` | Auth | Query history |
| `/scanner/company`, `/scanner/portfolio` | Auth | Shariah screening |
| `/tools/zakat` | Auth | Zakat calculator |
| `/documents` | Auth | Document analysis |
| `/scholars`, `/scholars/[slug]` | Auth | Scholar profiles |
| `/knowledge`, `/knowledge-graph` | Auth | Knowledge browser |
| `/evaluation` | Auth | Judge dashboard |
| `/settings` | Auth | Preferences and billing |
| `/admin` | Admin | Source management |

## Auth flow

1. Register at `/register` or sign in at `/login` (email/password or SSO)
2. JWT access token persisted in `authStore` (localStorage)
3. Incomplete onboarding redirects to `/onboarding`
4. Protected routes use `AuthGuard`; API requests send `Authorization: Bearer <token>` via `apiClient`

## Backend connection

- Dev: `next.config.mjs` rewrites `/api/:path*` → `${BACKEND_URL}/api/:path*`
- All API calls use prefix `/api/v1` via `src/services/apiClient.ts`
- See root [README.md](../README.md) for full stack setup

## Project layout

```
src/
├── app/           # App Router pages (thin wrappers)
├── features/      # Domain UI (chat, scanner, documents, …)
├── services/      # API clients
├── store/         # Zustand stores
├── components/    # Shared layout + Shadcn UI
└── lib/           # Utilities, i18n, constants
```
