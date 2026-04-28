FROM python:3.11-slim

# ── System dependencies ───────────────────────────────────────────────────────
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libglib2.0-0 \
    libgl1 \
    git \
    wget \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Point torch hub to a known in-image path — pre-downloaded at build time
ENV TORCH_HOME=/app/torch_cache

# ── Python dependencies (cached layer) ───────────────────────────────────────
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip "setuptools<70" wheel \
    && pip install --no-cache-dir -r requirements.txt

# ── NLTK data for CMU pronunciation dictionary ────────────────────────────────
RUN python -c "import nltk; nltk.download('cmudict', quiet=True)"

# ── Application source ────────────────────────────────────────────────────────
COPY app/ ./app/

# ── Model weights: mounted as volume at runtime — NOT baked into image ────────
# Volume mount point: /app/app/ml/weights
# Contains: wav2lip_gan.pth (124 MB), s3fd.pth (face detector)
RUN mkdir -p /app/app/ml/weights

# ── Pre-download face detection model so NO runtime download per-job ──────────
# face_detection library looks in $TORCH_HOME/hub/checkpoints/
# Baking it in eliminates 85MB download + OOM pressure on every inference call.
RUN mkdir -p /app/torch_cache/hub/checkpoints \
    && python -c "\
import urllib.request, os; \
url='https://www.adrianbulat.com/downloads/python-fan/s3fd-619a316812.pth'; \
dst='/app/torch_cache/hub/checkpoints/s3fd-619a316812.pth'; \
print('Downloading face detection model...'); \
urllib.request.urlretrieve(url, dst); \
print('Done:', os.path.getsize(dst), 'bytes')\
"

# ── Wav2Lip temp dir — must be writable at inference time ─────────────────────
RUN mkdir -p /app/app/ml/wav2lip_src/temp

# ── Tmp storage for uploads/outputs ──────────────────────────────────────────
RUN mkdir -p /app/tmp/uploads /app/tmp/outputs

# ── Non-root user for security ────────────────────────────────────────────────
RUN useradd -m -u 1000 phonemesync \
    && chown -R phonemesync:phonemesync /app
USER phonemesync

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", \
     "--workers", "1", "--log-level", "info"]
