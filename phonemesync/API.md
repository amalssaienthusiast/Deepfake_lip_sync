# PhonemeSync API — REST Contract

> **Auto-generated from AGENT_PROMPT.md Section 5.**
> This is the **single source of truth** for the frontend ↔ backend interface.
> M3 (Frontend) must mock against these schemas while M2/Amal build real endpoints.

**Base URL (dev):** `http://localhost:8000/api/v1`
**Base URL (prod):** `https://phonemesync-api.railway.app/api/v1`

---

## Endpoints Overview

| Method | Path | Purpose |
|---|---|---|
| `POST` | `/process` | Submit lip-sync job (async) |
| `GET` | `/status/{job_id}` | Poll job progress |
| `GET` | `/result/{job_id}` | Fetch synthesis result + landmarks |
| `GET` | `/phonemes/{job_id}` | Fetch phoneme timeline (innovation) |
| `GET` | `/health` | Server health check |

---

## POST /process

**Purpose:** Submit a lip-sync job. Returns `job_id` immediately. Processing is async.

**Request:** `multipart/form-data`

| Field | Type | Required | Description |
|---|---|---|---|
| `video_file` | File | ✅ | Face source — `.mp4`, `.avi`, `.mov`, `.jpg`, `.png` |
| `audio_file` | File | ✅ | Target speech — `.wav`, `.mp3`, `.aac` |

**Response 202 — Accepted:**
```json
{
  "job_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "status": "queued",
  "estimated_seconds": 45,
  "created_at": "2025-04-28T10:00:00Z"
}
```

**Response 422 — Validation Error:**
```json
{
  "error": "no_face_detected",
  "message": "Could not detect a face in the uploaded image/video.",
  "job_id": null
}
```

**Other 422 errors:** `invalid_file_type`, `file_too_large`, `inference_too_long`

---

## GET /status/{job_id}

**Purpose:** Poll job progress. Frontend should call every **2 seconds** while `status` is `queued` or `processing`.

**Response 200:**
```json
{
  "job_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "status": "processing",
  "progress": 40,
  "stage": "whisper",
  "error": null,
  "created_at": "2025-04-28T10:00:00Z",
  "updated_at": "2025-04-28T10:00:30Z"
}
```

**`status` values:** `queued` → `processing` → `done` | `failed`

**`stage` values (when `status === "processing"`):**

| Stage | Progress Range | What's Happening |
|---|---|---|
| `wav2lip` | 0 → 40 | GAN lip synthesis running |
| `whisper` | 40 → 60 | Phoneme extraction |
| `syncnet` | 60 → 80 | Per-frame confidence scoring |
| `mediapipe` | 80 → 95 | Lip landmark extraction |
| `done` | 100 | All stages complete |

**Response 404 — Job Not Found:**
```json
{
  "error": "job_not_found",
  "message": "Job not found. It may have expired or the ID is incorrect.",
  "job_id": null
}
```

---

## GET /result/{job_id}

**Purpose:** Fetch the full synthesis result. Only call when `status === "done"`.

**Response 200:**
```json
{
  "job_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "video_url": "/outputs/3fa85f64-5717-4562-b3fc-2c963f66afa6/synced.mp4",
  "original_video_url": "/outputs/3fa85f64-5717-4562-b3fc-2c963f66afa6/original.mp4",
  "duration_seconds": 8.4,
  "fps": 25.0,
  "resolution": [720, 1280],
  "syncnet_scores": [0.72, 0.81, 0.65, 0.78, 0.83],
  "syncnet_avg": 0.74,
  "syncnet_std": 0.08,
  "lip_landmarks": [
    {
      "frame_idx": 0,
      "timestamp_ms": 0,
      "lip_outer": [[120, 340], [125, 350], "..."],
      "lip_inner": [[123, 343], "..."],
      "lip_bbox": {"x": 110, "y": 330, "w": 80, "h": 40}
    }
  ],
  "processing_time_seconds": 38.2,
  "model_used": "wav2lip_gan"
}
```

> **Note for M3:** `video_url` is a relative path. Prefix with `NEXT_PUBLIC_API_BASE_URL` (not the `/api/v1` prefix) to get the full URL.
> Example: `https://phonemesync-api.railway.app/outputs/{job_id}/synced.mp4`

---

## GET /phonemes/{job_id}

**Purpose:** Fetch the phoneme timeline. This is the **innovation endpoint** that powers the PhonemeSync Visualizer canvas component.

**Response 200:**
```json
{
  "job_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "audio_duration_ms": 8400,
  "total_phonemes": 42,
  "timeline": [
    {
      "word": "hello",
      "word_start_ms": 120,
      "word_end_ms": 480,
      "phonemes": [
        {
          "symbol": "HH",
          "viseme_class": "glottal",
          "viseme_color": "#8B5CF6",
          "start_ms": 120,
          "end_ms": 200,
          "frame_start": 3,
          "frame_end": 5,
          "syncnet_confidence": 0.76
        },
        {
          "symbol": "AH1",
          "viseme_class": "mid_vowel",
          "viseme_color": "#F97316",
          "start_ms": 200,
          "end_ms": 340,
          "frame_start": 5,
          "frame_end": 8,
          "syncnet_confidence": 0.81
        },
        {
          "symbol": "L",
          "viseme_class": "alveolar",
          "viseme_color": "#22C55E",
          "start_ms": 340,
          "end_ms": 400,
          "frame_start": 8,
          "frame_end": 10,
          "syncnet_confidence": 0.79
        },
        {
          "symbol": "OW1",
          "viseme_class": "diphthong",
          "viseme_color": "#10B981",
          "start_ms": 400,
          "end_ms": 480,
          "frame_start": 10,
          "frame_end": 12,
          "syncnet_confidence": 0.85
        }
      ]
    }
  ],
  "viseme_summary": {
    "glottal":    {"count": 3,  "avg_confidence": 0.74},
    "mid_vowel":  {"count": 12, "avg_confidence": 0.81},
    "alveolar":   {"count": 8,  "avg_confidence": 0.77},
    "bilabial":   {"count": 5,  "avg_confidence": 0.79},
    "diphthong":  {"count": 6,  "avg_confidence": 0.83}
  }
}
```

### Viseme Color Reference (for canvas rendering)

| Class | Color | Phonemes |
|---|---|---|
| `silence` | `#94A3B8` | SIL, SP |
| `bilabial` | `#EC4899` | P, B, M |
| `labiodental` | `#F97316` | F, V |
| `dental` | `#EAB308` | TH, DH |
| `alveolar` | `#22C55E` | T, D, N, L, S, Z |
| `postalveolar` | `#14B8A6` | SH, ZH, CH, JH |
| `velar` | `#6366F1` | K, G, NG |
| `glottal` | `#8B5CF6` | HH |
| `front_vowel` | `#3B82F6` | IY, IH, EH, AE |
| `mid_vowel` | `#F97316` | AH, ER |
| `back_vowel` | `#EF4444` | AA, AO, OW, UH, UW |
| `diphthong` | `#10B981` | AW, AY, OY, EY |

---

## GET /health

**Response 200:**
```json
{
  "status": "ok",
  "app_env": "development",
  "device": "cpu",
  "models_loaded": true,
  "redis_connected": true
}
```

---

## Frontend Integration Notes (for M3)

### Polling Pattern
```typescript
async function pollUntilDone(jobId: string) {
  while (true) {
    const res = await fetch(`${API}/status/${jobId}`);
    const data = await res.json();
    
    updateProgressUI(data.progress, data.stage);
    
    if (data.status === 'done') {
      return await fetchResult(jobId);
    }
    if (data.status === 'failed') {
      throw new Error(data.error);
    }
    
    await sleep(2000); // poll every 2 seconds
  }
}
```

### File Upload Pattern
```typescript
const formData = new FormData();
formData.append('video_file', videoFile);  // File object
formData.append('audio_file', audioFile);  // File object

const res = await fetch(`${API}/process`, {
  method: 'POST',
  body: formData,
  // Do NOT set Content-Type header — browser sets multipart boundary automatically
});
```

### Canvas Timeline Rendering
For each `phoneme` in the timeline:
- `x = (phoneme.start_ms / audio_duration_ms) * canvasWidth`
- `width = ((phoneme.end_ms - phoneme.start_ms) / audio_duration_ms) * canvasWidth`
- `height = phoneme.syncnet_confidence * maxBlockHeight`
- `fillStyle = phoneme.viseme_color`
- Playhead: `x = (video.currentTime * 1000 / audio_duration_ms) * canvasWidth`

---

*Last updated: 2025-04-28 | PhonemeSync v1.0 | IBM Sprint*
