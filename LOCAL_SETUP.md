# 🚀 PhonemeSync Local Setup Guide

## Current Status

✅ **Backend**: Running on http://localhost:8000
- Python 3.9.6 with FastAPI
- Health check: OK
- Development mode enabled with auto-reload
- Redis: Optional (job queue, currently not needed for basic testing)

⏳ **Frontend**: Ready to start (needs Node.js)
- Next.js 14.2.35 configured
- Environment file ready at `.env.local`
- All dependencies specified in `package.json`

---

## Prerequisites Installation

### Option 1: Using Homebrew (macOS recommended)

```bash
# Install Homebrew if not already installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Node.js (includes npm)
brew install node

# Install pnpm (recommended package manager for this project)
npm install -g pnpm
```

### Option 2: Using Node.js Installer
1. Download from https://nodejs.org/ (LTS version recommended)
2. Run the installer
3. Then install pnpm:
   ```bash
   npm install -g pnpm
   ```

### Verify Installation

```bash
node --version    # Should be 18.x or higher
npm --version     # Should be 9.x or higher
pnpm --version    # Should be 8.x or higher
```

---

## Quick Start

### 1. Backend is Already Running ✓

```bash
# Check backend health
curl http://localhost:8000/health

# Expected response:
# {"status":"ok","app_env":"development","device":"cpu","models_loaded":false,"redis_connected":false}
```

### 2. Start Frontend

```bash
cd phonemesync/frontend

# Install dependencies (first time only)
pnpm install

# Start development server
pnpm dev
```

The frontend will start on **http://localhost:3000**

---

## Local Development Workflow

### Terminal 1: Backend (Already running)
```bash
cd phonemesync/backend
. venv/bin/activate
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Status: ✅ RUNNING

### Terminal 2: Frontend
```bash
cd phonemesync/frontend
pnpm install        # First time only
pnpm dev
```

Once running, open browser to **http://localhost:3000**

---

## Available URLs

| Service | URL | Purpose |
|---------|-----|---------|
| Frontend | http://localhost:3000 | Main UI |
| Backend API | http://localhost:8000 | API endpoints |
| Backend Health | http://localhost:8000/health | Status check |
| API Docs | http://localhost:8000/docs | Swagger UI |
| API ReDoc | http://localhost:8000/redoc | Alternative API docs |

---

## Testing the Full Pipeline

### 1. Upload Files
- Go to http://localhost:3000
- Select a face image (JPG/PNG) or video (MP4/MOV)
- Select an audio file (WAV/MP3)
- Click "Synthesize Lip Sync"

### 2. Monitor Progress
- You'll be redirected to `/processing/{jobId}`
- Watch the progress ring and stage tracker
- Polls every 2 seconds

### 3. View Results
- Once complete, you'll see `/results/{jobId}`
- Watch side-by-side video comparison
- View phoneme timeline with confidence scores
- Download the synced video

---

## Backend API Testing

### Health Check
```bash
curl http://localhost:8000/health
```

### Job Endpoints (Manual Testing)
See [API.md](phonemesync/API.md) for full endpoint documentation.

```bash
# List all endpoints
curl http://localhost:8000/docs
```

---

## Troubleshooting

### Frontend Won't Start
**Problem**: "Cannot find module 'next'"
```bash
# Solution: Reinstall dependencies
rm -rf node_modules pnpm-lock.yaml
pnpm install
```

### Backend Connection Error
**Problem**: "Failed to connect to http://localhost:8000"
```bash
# Solution: Verify backend is running
curl http://localhost:8000/health

# If not running, start it:
cd phonemesync/backend
. venv/bin/activate
python -m uvicorn app.main:app --port 8000
```

### Port Already in Use
**Backend port 8000 taken**:
```bash
# Find process using port 8000
lsof -i :8000

# Kill it:
kill -9 <PID>

# Or use different port:
python -m uvicorn app.main:app --port 8001
# Then update frontend .env.local: NEXT_PUBLIC_API_URL=http://localhost:8001
```

**Frontend port 3000 taken**:
```bash
# Find process using port 3000
lsof -i :3000

# Kill it or use different port:
pnpm dev -- -p 3001
```

### NLTK Error in Backend
**Problem**: "nltk_data not found"
- This is a warning and doesn't affect basic functionality
- To fix, run in backend Python: 
  ```python
  import nltk
  nltk.download('averaged_perceptron_tagger')
  ```

### Redis Connection Warning
**Problem**: "Error 61 connecting to localhost:6379"
- This is expected if Redis isn't running
- Redis is only needed for job persistence across restarts
- Basic functionality works without it

---

## Development Tips

### Frontend Code Changes
- All code in `phonemesync/frontend/src/` auto-reloads with `pnpm dev`
- Check browser console (F12) for React errors
- Visit http://localhost:3000 to see changes

### Backend Code Changes
- All code in `phonemesync/backend/app/` auto-reloads with `--reload` flag
- Check terminal for FastAPI startup logs
- API docs auto-update at http://localhost:8000/docs

### View TypeScript Errors
```bash
cd phonemesync/frontend
npx tsc --noEmit
```

### Lint Frontend Code
```bash
cd phonemesync/frontend
pnpm lint
```

---

## Next Steps

1. ✅ Backend running
2. 📦 Install Node.js if needed
3. 🚀 Start frontend with `pnpm dev`
4. 🎨 Open http://localhost:3000
5. 📝 Upload test files
6. 🎬 Watch it synthesize!

---

## Getting Help

- Backend logs: Check terminal where `uvicorn` is running
- Frontend logs: Check browser console (F12) and terminal where `pnpm dev` is running
- API documentation: http://localhost:8000/docs
- Project README: [phonemesync/README.md](phonemesync/README.md)
- Frontend guide: [phonemesync/frontend/FRONTEND_GUIDE.md](phonemesync/frontend/FRONTEND_GUIDE.md)
