# Frontend - React Dashboard

## Overview

React + TypeScript web dashboard for:
- Browsing video library
- Triggering desktop annotation tool
- Monitoring training runs
- Managing trained models
- Viewing activity history

## Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── VideoLibrary/
│   │   │   ├── VideoGrid.tsx
│   │   │   ├── VideoCard.tsx
│   │   │   └── VideoFilters.tsx
│   │   ├── Training/
│   │   │   ├── TrainingDashboard.tsx
│   │   │   ├── TrainingConfig.tsx
│   │   │   ├── LiveLogs.tsx
│   │   │   └── ModelComparison.tsx
│   │   ├── History/
│   │   │   ├── ActivityTimeline.tsx
│   │   │   └── UserStats.tsx
│   │   └── Auth/
│   │       ├── LoginPage.tsx
│   │       └── DesktopAppBanner.tsx
│   ├── hooks/
│   │   ├── useRealtimeVideos.ts
│   │   ├── useTrainingLogs.ts
│   │   └── useAuth.ts
│   ├── lib/
│   │   ├── supabase.ts
│   │   └── api.ts
│   ├── App.tsx
│   └── main.tsx
├── public/
├── package.json
└── .env.example
```

## Setup

### 1. Install Dependencies

```bash
npm install
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your credentials
```

Required environment variables:
- `VITE_SUPABASE_URL` - Your Supabase project URL
- `VITE_SUPABASE_ANON_KEY` - Supabase anon key
- `VITE_API_URL` - Backend API URL (default: http://localhost:8000)

### 3. Run Development Server

```bash
npm run dev
```

Dashboard runs at `http://localhost:3000`

## Tech Stack

- **Framework:** React 18
- **Language:** TypeScript
- **Build:** Vite
- **Styling:** TailwindCSS
- **State:** React Query + Zustand
- **Auth:** Supabase Auth
- **Real-time:** Supabase Realtime

## Development

### Adding New Components

1. Create component in `src/components/`
2. Add to appropriate section (VideoLibrary, Training, etc.)
3. Import in parent component or route

### Styling

Using TailwindCSS utility classes. See [TailwindCSS docs](https://tailwindcss.com/docs).

### Testing

```bash
npm run test
```

## Build for Production

```bash
npm run build
```

Output in `dist/` directory.

## Deployment

See [docs/deployment.md](../docs/deployment.md) for deployment instructions.
