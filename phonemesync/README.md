# PhonemeSync

> Audio-driven lip synthesis with real-time phoneme confidence visualization.
> IBM Project · 24hr Sprint · Wav2Lip + Whisper + SyncNet + MediaPipe.

## What it does

1. Takes a face image/video + target audio
2. Synthesizes lip-synced video with **Wav2Lip GAN**
3. Extracts phoneme timestamps with **OpenAI Whisper**
4. Maps phonemes → 12 viseme classes (CMU pronunciation standard)
5. Scores per-frame sync confidence with **SyncNet**
6. Extracts lip landmarks per frame with **MediaPipe FaceMesh**
7. Returns all as structured JSON + video via REST API

**Innovation:** No existing open-source tool exposes phoneme-to-viseme alignment alongside per-frame sync confidence as a structured API. PhonemeSync does both.

## Quick Start (local dev)

```bash
# 1. Clone and enter
cd phonemesync/backend

# 2. Copy env
cp .env.example .env

# 3. Download model weights (see AGENT_PROMPT.md §1.3)
mkdir -p app/ml/weights
# Download wav2lip_gan.pth and s3fd.pth into app/ml/weights/

# 4. Clone Wav2Lip source
cd app/ml
git clone https://github.com/Rudrabha/Wav2Lip.git wav2lip_src
cd ../..

# 5. Docker Compose (recommended)
docker compose up --build

# 6. Verify
curl http://localhost:8000/health
```

## API Endpoints

| Method | Path | Description |
|---|---|---|
| POST | `/api/v1/process` | Submit job |
| GET | `/api/v1/status/{id}` | Poll progress |
| GET | `/api/v1/result/{id}` | Fetch synced video |
| GET | `/api/v1/phonemes/{id}` | Fetch phoneme timeline |
| GET | `/health` | Health check |

See [API.md](../API.md) for full contract.

## Tech Stack

| Layer | Technology |
|---|---|
| API | FastAPI + Uvicorn |
| ML Lip Sync | Wav2Lip GAN |
| Phoneme Extraction | OpenAI Whisper (base) |
| Sync Scoring | SyncNet (discriminator proxy) |
| Lip Landmarks | MediaPipe FaceMesh |
| Job Queue | Redis |
| Deploy | Railway (backend) · Vercel (frontend) |

## Research Benchmarks

| Model | SyncNet Score ↑ | FID ↓ |
|---|---|---|
| Wav2Lip (ours) | 6.37 | 70.42 |
| LatentSync (SOTA) | 7.62 | 25.13 |

Wav2Lip chosen for 24hr prototype: runs on CPU, 1-command install.
LatentSync documented as the v2 upgrade path.

## Ethical Note

PhonemeSync is a research prototype exploring audio-visual synchronization. The same phoneme confidence visualization that makes synthesis transparent is a forensic tool for detecting lip-sync manipulation. Anti-spoofing detection module is on the roadmap (NexDesk integration).
