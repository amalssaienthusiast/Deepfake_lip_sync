# PhonemeSync — Complete Setup & Demo Guide
> IBM Hackathon Edition | Works on macOS · Windows · Linux

---

## Part 1: Prerequisites (All Platforms)

### 1.1 Software Requirements

| Software | Version | Download |
|---|---|---|
| **Docker Desktop** | Latest | https://www.docker.com/products/docker-desktop |
| **Node.js** | v18.x (not v16, not v20) | https://nodejs.org/en/download |
| **pnpm** | Latest | `npm install -g pnpm` |
| **Git** | Latest | https://git-scm.com/downloads |

> [!IMPORTANT]
> Docker Desktop must be running **before** any `docker compose` commands.

---

## Part 2: Platform-Specific Setup

### 2.1 macOS Setup

**Step 1 — Increase Docker Memory**
1. Open **Docker Desktop** → ⚙️ **Settings** → **Resources**
2. Set **Memory** to **6 GB** minimum (8 GB recommended)
3. Click **Apply & Restart**

**Step 2 — Verify tools**
```bash
docker --version       # Docker version 24+
node --version         # v18.x
npm install -g pnpm
pnpm --version
git --version
```

---

### 2.2 Windows Setup

**Step 1 — Enable WSL2 (if not done)**
Open PowerShell as Administrator:
```powershell
wsl --install
wsl --set-default-version 2
```
Restart your PC when prompted.

**Step 2 — Increase WSL2 Memory** *(critical — default is 50% of RAM)*

Create/edit the file `C:\Users\<YourUsername>\.wslconfig`:
```ini
[wsl2]
memory=8GB
processors=4
```
Then in PowerShell:
```powershell
wsl --shutdown
```
Then restart Docker Desktop.

**Step 3 — Increase Docker Desktop Memory**
1. Open **Docker Desktop** → ⚙️ **Settings** → **Resources** → **Advanced**
2. Set **Memory** to **6 GB** minimum
3. Click **Apply & Restart**

**Step 4 — Verify tools in PowerShell or Git Bash**
```powershell
docker --version
node --version    # must be v18.x
npm install -g pnpm
pnpm --version
git --version
```

---

### 2.3 Linux Setup

**Step 1 — Install Docker Engine**
```bash
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
newgrp docker
```

**Step 2 — Install Docker Compose plugin**
```bash
sudo apt-get install docker-compose-plugin
```

**Step 3 — Linux has no memory VM cap** — Docker uses your real system RAM. Just ensure you have **6+ GB free** before running.

---

## Part 3: Project Setup (All Platforms)

### 3.1 Clone the Repository
```bash
git clone https://github.com/amalssaienthusiast/Deepfake_lip_sync.git
cd Deepfake_lip_sync/phonemesync
```

### 3.2 Download ML Model Weights

> [!CAUTION]
> Without these files the backend will start but ALL jobs will fail. This step is mandatory.

You need **2 files**:

| File | Size | What it does |
|---|---|---|
| `wav2lip_gan.pth` | ~436 MB | The main lip-sync GAN model |
| `s3fd.pth` | ~86 MB | Face detection model |

**Download links:**
- `wav2lip_gan.pth` → https://github.com/Rudrabha/Wav2Lip/releases (Wav2Lip GAN checkpoint)
- `s3fd.pth` → https://www.adrianbulat.com/downloads/python-fan/s3fd-619a316812.pth

> Rename `s3fd-619a316812.pth` → `s3fd.pth` after downloading.

**Place both files here:**
```
Deepfake_lip_sync/
  phonemesync/
    backend/
      app/
        ml/
          weights/        ← PUT BOTH FILES HERE
            wav2lip_gan.pth
            s3fd.pth
```

```bash
# Verify both files exist:
ls phonemesync/backend/app/ml/weights/
# Expected output: s3fd.pth   wav2lip_gan.pth
```

### 3.3 Configure the Backend Environment
```bash
cd phonemesync/backend
cp .env.example .env
```
The defaults in `.env` work out of the box — no changes needed for local demo.

### 3.4 Start the Backend
```bash
# From inside phonemesync/backend/
docker compose up -d --build
```

This will:
1. Build the Python 3.11 Docker image (~5–10 min first time)
2. Download Whisper `base` model (~140 MB) automatically
3. Start FastAPI on `http://localhost:8000`
4. Start Redis on port `6379`

**Wait ~30 seconds then verify:**
```bash
curl http://localhost:8000/health
```
Expected response:
```json
{"status":"ok","models_loaded":true,"redis_connected":true}
```

> [!NOTE]
> On first build, Docker downloads ~1 GB of Python packages and ML libraries. Subsequent starts take under 10 seconds.

### 3.5 Start the Frontend
```bash
# In a NEW terminal tab:
cd phonemesync/frontend
pnpm install
pnpm dev
```
Open your browser at **http://localhost:3000**

---

## Part 4: How to Run a Demo

### 4.1 What makes a good demo input

**Face video / image requirements:**
- ✅ Clear frontal face (looking at camera)
- ✅ Good lighting, no heavy shadows
- ✅ Single person in frame
- ✅ Formats: `.mp4`, `.jpg`, `.png`
- ✅ Duration: 5–30 seconds (longer = slower)
- ❌ Avoid: multiple faces, profile shots, dark/blurry images

**Audio requirements:**
- ✅ Clear speech, minimal background noise
- ✅ Formats: `.mp3`, `.wav`
- ✅ Duration should match or be shorter than video
- ✅ 5–30 seconds is ideal for a demo

### 4.2 Step-by-step demo flow

1. **Open** `http://localhost:3000`
2. **Drag** a face image or video into the **left drop zone**
3. **Drag** an audio `.mp3` or `.wav` file into the **right drop zone**
4. **Click** "Synthesize Lip Sync"
5. You'll see a **live progress bar** cycling through 4 stages:
   - 🔵 Lip Synthesis (Wav2Lip GAN) — 0→40%
   - 🟢 Phoneme Extraction (Whisper) — 40→60%
   - 🟠 Sync Scoring (SyncNet) — 60→80%
   - 🟣 Landmark Detection (MediaPipe) — 80→100%
6. Results screen shows:
   - Side-by-side video comparison (original vs lip-synced)
   - **PhonemeSync Timeline** — phoneme-by-phoneme sync confidence chart
   - **SyncNet heatmap** overlay on the face

### 4.3 Typical processing times (CPU only)

| Input length | Approximate time |
|---|---|
| 5 seconds | ~1–2 minutes |
| 15 seconds | ~3–5 minutes |
| 30 seconds | ~8–12 minutes |

> [!TIP]
> For a live hackathon demo, prepare a **pre-processed result** to show instantly. Submit a job in advance, let it finish, and use that URL for your live presentation. Then show the upload flow as a secondary demo.

### 4.4 IBM Judge Demo Script

**Suggested talking points during demo:**

1. **"This is the Upload Screen"** — Point out the drag-and-drop UX, dual file upload
2. **"We're now submitting to our FastAPI backend"** — Show the network tab briefly
3. **"This is real-time polling"** — The progress bar is polling `/api/v1/status/{job_id}` every 2 seconds
4. **"Four ML stages run in sequence"** — Explain: Wav2Lip GAN → OpenAI Whisper → SyncNet → MediaPipe
5. **"PhonemeSync Timeline"** — This is the novel contribution: per-phoneme sync confidence mapped to viseme classes
6. **"SyncNet heatmap"** — Frame-by-frame lip sync confidence overlay

---

## Part 5: Troubleshooting

| Error | Cause | Fix |
|---|---|---|
| `ERR_CONNECTION_REFUSED` on port 8000 | Docker not running or API crashed | Run `docker compose up -d` from `backend/` |
| `exit -9` / OOM kill | Docker VM out of memory | Increase Docker memory to 6 GB+ |
| `wav2lip_weights_missing` | `.pth` files not in `app/ml/weights/` | Download and place both `.pth` files |
| `Face not detected` error | Face not visible in video/image | Use a clear frontal face photo |
| Health check shows `models_loaded: false` | Whisper model still downloading | Wait 60 seconds and retry |
| CORS error in browser console | Frontend URL not in CORS list | Check `CORS_ORIGINS` in `docker-compose.yml` |
| `pnpm: command not found` | pnpm not installed | Run `npm install -g pnpm` |

### Check backend logs anytime:
```bash
cd phonemesync/backend
docker compose logs --tail=50 api
```

### Restart everything cleanly:
```bash
cd phonemesync/backend
docker compose restart api
```

### Full reset (if something is very broken):
```bash
cd phonemesync/backend
docker compose down --volumes
docker compose up -d --build
```

---

## Part 6: Quick Reference

```bash
# ── BACKEND ─────────────────────────────────
cd phonemesync/backend
docker compose up -d --build      # start (first time)
docker compose up -d              # start (subsequent)
docker compose logs --tail=30 api # check logs
docker compose down               # stop
curl http://localhost:8000/health # verify

# ── FRONTEND ────────────────────────────────
cd phonemesync/frontend
pnpm install    # first time only
pnpm dev        # start dev server → http://localhost:3000
```

---

## Part 7: Production Deployment (Vercel + Container Host)

PhonemeSync requires two deployments:

- **Frontend** → Vercel
- **Backend** → a container host with Redis (Railway / Render / Fly)

### 7.1 Backend (FastAPI + Redis)

1. Provision **Redis** and a persistent volume for `/app/tmp`.
2. Upload model weights to a volume mounted at `/app/app/ml/weights`:
   - `wav2lip_gan.pth`
   - `s3fd.pth`
3. Set environment variables:
   - `APP_ENV=production`
   - `REDIS_URL=redis://...`
   - `UPLOAD_DIR=/app/tmp/uploads`
   - `OUTPUT_DIR=/app/tmp/outputs`
   - `DEVICE=cpu` (or `cuda` if GPU)
   - `CORS_ORIGINS=https://your-vercel-domain.vercel.app`
4. Deploy using the existing `backend/Dockerfile`.
5. Verify `GET /health` returns `"status":"ok"` and that `/outputs/...` URLs load.

### 7.2 Frontend (Vercel)

1. Set **Root Directory** to `phonemesync/frontend`.
2. Use **Node.js 18** and **pnpm**.
3. Add `NEXT_PUBLIC_API_URL=https://your-backend.example.com`.
4. Deploy, then upload a sample face + audio to validate end-to-end.
