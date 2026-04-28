# PhonemeSync: Complete Setup & Execution Guide

This guide walks you through the complete process of bringing the **PhonemeSync** project online locally. The project is split into a **Python/FastAPI Backend** (powered by Docker) and a **Next.js 14 Frontend**.

---

## 1. Prerequisites

Before starting, ensure you have the following installed on your machine (macOS/Linux):
1. **Docker Desktop** (or Docker Engine + Docker Compose)
2. **Node.js** (v18.x recommended)
3. **pnpm** (`npm install -g pnpm`)
4. **Git**

---

## 2. Backend Setup (Docker + ML Models)

The backend handles Wav2Lip GAN inference, Whisper transcription, SyncNet scoring, and MediaPipe landmark detection. It requires heavy ML weights to be downloaded manually before starting the Docker container.

### Step 2.1: Environment Setup
Navigate to the backend directory and copy the environment template:
```bash
cd phonemesync/backend
cp .env.example .env
```

### Step 2.2: Download ML Weights
The backend expects specific model weights to be present in the `app/ml/weights/` directory.

1. Create the weights directory:
   ```bash
   mkdir -p app/ml/weights
   ```
2. Download the required weights. 
   - **Wav2Lip GAN (`wav2lip_gan.pth`)**: Download from the official Wav2Lip repository or your provided hackathon storage bucket.
   - **Face Detection (`s3fd.pth`)**: Download the S3FD face detector model.
3. Place both files inside the `phonemesync/backend/app/ml/weights/` folder.

> **Important:** The Dockerfile uses a volume mount (`- ./app/ml/weights:/app/ml/weights`) so the container can access these large files without baking them into the image.

### Step 2.3: Start the Backend Services
With Docker Desktop running, start the API and the Redis job queue:

```bash
# From inside the phonemesync/backend directory:
docker compose up -d --build
```

This command will:
1. Build the Python 3.11 API image.
2. Download required system dependencies (ffmpeg, etc.).
3. Start the Redis container for task queuing.
4. Start the FastAPI server on port 8000.

### Step 2.4: Verify Backend Health
Once the containers are running, wait a few moments and verify the health check:
```bash
curl http://localhost:8000/health
```
You should receive: `{"status": "ok"}`.

---

## 3. Frontend Setup (Next.js 14)

The frontend is a Next.js 14 application using the App Router, Tailwind CSS, and Zustand.

### Step 3.1: Environment Setup
Navigate to the frontend directory:
```bash
cd phonemesync/frontend
```
*(The `.env.local` file was automatically generated during scaffolding and already points to `http://localhost:8000`)*.

### Step 3.2: Install Dependencies
If you haven't already, install the Node packages using `pnpm`:
```bash
pnpm install
```

### Step 3.3: Start the Development Server
Start the Next.js local development server:
```bash
pnpm dev
```

### Step 3.4: Open the App
Open your browser and navigate to:
**[http://localhost:3000](http://localhost:3000)**

You should see the dark-themed PhonemeSync upload screen.

---

## 4. How to Test the Pipeline

1. **Upload Media**: On the frontend at `localhost:3000`, drag and drop a face image (e.g., a `.jpg` of a person looking forward) into the left box, and a speech audio file (`.wav` or `.mp3`) into the right box.
2. **Synthesize**: Click the "Synthesize Lip Sync" button.
3. **Watch Progress**: You will be redirected to the processing screen. The system will poll the backend every 2 seconds, displaying progress through the four ML stages:
   - *Lip Synthesis (Wav2Lip)*
   - *Phoneme Extraction (Whisper)*
   - *Sync Scoring (SyncNet)*
   - *Landmark Detection (MediaPipe)*
4. **View Results**: Once complete, you will land on the Results dashboard. 
   - You can watch the synchronized video side-by-side with the original.
   - The lip bounding box and heatmap overlay will track the face.
   - The **Phoneme Timeline** at the bottom will display individual phonemes, colored by viseme class, with heights corresponding to the AI's confidence in the lip synchronization at that exact millisecond.

---

## 5. Troubleshooting Common Issues

- **`NoFaceDetectedError`**: If the Wav2Lip inference fails with this error, ensure the uploaded image/video has a clear, well-lit face looking at the camera.
- **Docker Build Fails on NLTK/OpenCV**: The Dockerfile installs necessary `libgl1` and `ffmpeg` libraries. Ensure you have a stable internet connection during the initial `docker compose build`.
- **CORS Errors in Browser**: If the frontend console shows CORS errors, ensure the Next.js `rewrites` are working properly (they proxy `/api/*` to `localhost:8000/api/*`). The frontend should make calls to `/api/v1/process`.
- **Canvas Overlay Misaligned**: The heatmap overlay relies on `ResizeObserver`. If the browser window is rapidly resized during playback, pause and play the video to trigger a coordinate refresh.
