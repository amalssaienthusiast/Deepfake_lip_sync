# Frontend Setup & Deployment Guide

## Quick Start

### 1. Prerequisites
Ensure you have installed:
- **Node.js** 18.x or higher (`node --version`)
- **pnpm** (`npm install -g pnpm`)

### 2. Installation

```bash
cd phonemesync/frontend
pnpm install
```

This installs all dependencies from `package.json`:
- **Next.js 14.2.35** - React framework with App Router
- **React 18** - UI library
- **TypeScript 5** - Type-safe development
- **Tailwind CSS 3.4.1** - Utility-first styling
- **Zustand 5.0.12** - Global state management
- **TanStack React Query 5.100.5** - Server state management
- **Axios 1.15.2** - HTTP client
- **Radix UI** - Unstyled, accessible components
- **Lucide React** - Icon library
- **Framer Motion 12.38.0** - Animation library
- **Sonner 2.0.7** - Toast notifications

### 3. Environment Configuration

Create `.env.local` with:
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_NAME=PhonemeSync
```

The `NEXT_PUBLIC_` prefix makes variables accessible in the browser.

### 4. Development Server

```bash
pnpm dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

## Project Structure

```
src/
├── app/                      # Next.js App Router pages
│   ├── page.tsx             # Redirect to /upload
│   ├── layout.tsx           # Root layout with metadata & toaster
│   ├── globals.css          # Global styles & animations
│   ├── upload/page.tsx      # Upload form page
│   ├── processing/[jobId]/  # Job progress tracking
│   └── results/[jobId]/     # Results visualization
│
├── components/
│   ├── upload/              # File upload components
│   ├── processing/          # Progress tracking UI
│   ├── results/             # Results display components
│   └── phoneme/             # Timeline & phoneme visualization
│
├── lib/
│   ├── api.ts              # Backend API client (typed)
│   ├── store.ts            # Zustand global state
│   ├── constants.ts        # App-wide constants
│   ├── utils.ts            # Helper utilities
│
├── hooks/
│   ├── useJobPolling.ts    # Poll job status
│   ├── usePhonemeData.ts   # Process phoneme timeline
│   └── useVideoSync.ts     # Sync video playhead
│
└── types/
    └── api.ts              # TypeScript types for backend responses
```

## Key Features

### 1. File Upload (`/upload`)
- Drag-and-drop zone for face image/video
- Drag-and-drop zone for target audio
- File validation (type, size)
- Automatic job submission

### 2. Progress Tracking (`/processing/[jobId]`)
- Real-time status polling (every 2 seconds)
- Visual progress ring (0-100%)
- Processing stage tracker (Wav2Lip → Whisper → SyncNet → MediaPipe)
- Error handling with retry

### 3. Results Page (`/results/[jobId]`)
- Side-by-side original vs lip-synced video comparison
- SyncNet confidence metrics (avg, std, per-frame)
- Interactive phoneme timeline with hover details
- Viseme color legend
- Video download button

### 4. Phoneme Timeline
- Frame-level phoneme annotations
- Viseme classes with semantic colors
- Confidence scores (high, medium, low)
- Interactive scrubbing and playhead sync

## Building for Production

### Development Build
```bash
pnpm build
```

Creates optimized production build in `.next/` directory.

### Run Production Build
```bash
pnpm start
```

Starts the production server on port 3000.

### Docker Deployment

Create a `Dockerfile` in the frontend directory:
```dockerfile
# Build stage
FROM node:18-alpine AS builder
WORKDIR /app
COPY package.json pnpm-lock.yaml ./
RUN npm install -g pnpm && pnpm install
COPY . .
RUN pnpm build

# Runtime stage
FROM node:18-alpine
WORKDIR /app
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
COPY --from=builder /app/package.json ./package.json
RUN npm install -g pnpm && pnpm install --prod

EXPOSE 3000
CMD ["pnpm", "start"]
```

## Linting & Type Checking

```bash
# Lint with ESLint
pnpm lint

# Type check with TypeScript
npx tsc --noEmit
```

## API Integration

All backend calls are centralized in `src/lib/api.ts`:

```typescript
import { submitJob, getJobStatus, getJobResult, getPhonemes } from '@/lib/api'

// Submit a new job
const response = await submitJob(faceFile, audioFile)

// Poll job status
const status = await getJobStatus(jobId)

// Get final result
const result = await getJobResult(jobId)

// Get phoneme timeline
const phonemes = await getPhonemes(jobId)
```

All functions are **fully typed** and return backend schema types.

## State Management

Global state is managed with Zustand (`src/lib/store.ts`):

```typescript
import { useStore } from '@/lib/store'

// Access state
const jobId = useStore((s) => s.jobId)
const faceFile = useStore((s) => s.faceFile)

// Update state
const setJobId = useStore((s) => s.setJobId)
setJobId('new-job-123')

// Reset all state
const reset = useStore((s) => s.reset)
reset()
```

## Troubleshooting

### API Connection Errors
- Ensure backend is running at `http://localhost:8000`
- Check `.env.local` for correct `NEXT_PUBLIC_API_URL`
- Verify CORS is enabled on backend

### Build Errors
- Delete `.next/` and `node_modules/`
- Run `pnpm install` again
- Clear pnpm cache: `pnpm store prune`

### Type Errors
- Ensure backend types in `src/types/api.ts` match backend schemas
- Run `npx tsc --noEmit` to check all type errors
- Update types if backend schema changes

## Performance Optimization

- **Image optimization**: Next.js automatically optimizes images
- **Code splitting**: Next.js chunks components by route
- **Font optimization**: Geist font is self-hosted
- **CSS optimization**: Tailwind removes unused CSS in production

## Browser Support

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- Modern browsers with ES2020+ support

## Additional Resources

- [Next.js Documentation](https://nextjs.org/docs)
- [React Documentation](https://react.dev)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [TypeScript Documentation](https://www.typescriptlang.org/docs)
