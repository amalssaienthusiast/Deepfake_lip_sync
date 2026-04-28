"""All Pydantic v2 request/response schemas for PhonemeSync API.

SINGLE SOURCE OF TRUTH — import from here, never redefine schemas in routers.
Follows spec Section 5 (API contracts) and Section 6 (viseme classes).
"""
from __future__ import annotations

import enum
from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field


# ── Enums ─────────────────────────────────────────────────────────────────────

class JobStatus(str, enum.Enum):
    """Lifecycle states for an async processing job."""
    queued     = "queued"
    processing = "processing"
    done       = "done"
    failed     = "failed"


class ProcessingStage(str, enum.Enum):
    """Which ML stage the worker is currently executing."""
    wav2lip    = "wav2lip"
    whisper    = "whisper"
    syncnet    = "syncnet"
    mediapipe  = "mediapipe"
    done       = "done"


class VisemeClass(str, enum.Enum):
    """12 viseme classes derived from CMU pronunciation standard."""
    silence       = "silence"
    bilabial      = "bilabial"
    labiodental   = "labiodental"
    dental        = "dental"
    alveolar      = "alveolar"
    postalveolar  = "postalveolar"
    velar         = "velar"
    glottal       = "glottal"
    front_vowel   = "front_vowel"
    mid_vowel     = "mid_vowel"
    back_vowel    = "back_vowel"
    diphthong     = "diphthong"


# ── Shared Base ───────────────────────────────────────────────────────────────

class PhonemeySyncBase(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
    )


# ── Job Submit Response ───────────────────────────────────────────────────────

class JobSubmitResponse(PhonemeySyncBase):
    """Response to POST /process — returned immediately (async job)."""

    job_id: str = Field(..., description="UUID v4 job identifier")
    status: JobStatus = Field(default=JobStatus.queued)
    estimated_seconds: int = Field(
        default=45,
        description="Rough server-side estimate of processing time",
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)


# ── Job Status Response ───────────────────────────────────────────────────────

class JobStatusResponse(PhonemeySyncBase):
    """Response to GET /status/{job_id} — polled by frontend every 2s."""

    job_id: str
    status: JobStatus
    progress: int = Field(default=0, ge=0, le=100, description="0–100 progress %")
    stage: Optional[ProcessingStage] = None
    error: Optional[str] = None
    created_at: datetime
    updated_at: datetime


# ── Result Response ──────────────────────────────────────────────────────────

class LipBbox(PhonemeySyncBase):
    """Bounding box of the lip region in pixel space."""

    x: int
    y: int
    w: int
    h: int


class LipLandmarkFrame(PhonemeySyncBase):
    """Per-frame lip landmark data from MediaPipe FaceMesh."""

    frame_idx: int = Field(..., description="0-indexed frame number")
    timestamp_ms: int = Field(..., description="Frame timestamp in milliseconds")
    lip_outer: list[list[int]] = Field(
        ..., description="Outer lip landmark pixel coordinates [[x,y], ...]"
    )
    lip_inner: list[list[int]] = Field(
        ..., description="Inner lip landmark pixel coordinates [[x,y], ...]"
    )
    lip_bbox: LipBbox


class ResultResponse(PhonemeySyncBase):
    """Response to GET /result/{job_id} — full synthesis result."""

    job_id: str
    video_url: str = Field(..., description="Relative URL to the synced output video")
    original_video_url: str = Field(..., description="Relative URL to the original video")
    duration_seconds: float
    fps: float
    resolution: list[int] = Field(..., description="[width, height] in pixels")

    # SyncNet confidence
    syncnet_scores: list[float] = Field(
        default_factory=list,
        description="Per-frame confidence scores in [0.0, 1.0]",
    )
    syncnet_avg: float = Field(default=0.0, ge=0.0, le=1.0)
    syncnet_std: float = Field(default=0.0, ge=0.0)

    # Lip landmarks
    lip_landmarks: list[LipLandmarkFrame] = Field(default_factory=list)

    processing_time_seconds: float
    model_used: str = Field(default="wav2lip_gan")


# ── Phonemes Response ─────────────────────────────────────────────────────────

class PhonemeEntry(PhonemeySyncBase):
    """A single phoneme within a word — the atomic unit of the timeline."""

    symbol: str = Field(..., description="CMU/ARPAbet phoneme symbol e.g. 'AH1'")
    viseme_class: VisemeClass
    viseme_color: str = Field(..., description="Hex color for canvas rendering")

    start_ms: int = Field(..., ge=0)
    end_ms: int = Field(..., ge=0)
    frame_start: int = Field(..., ge=0, description="Inclusive start frame index")
    frame_end: int = Field(..., ge=0, description="Inclusive end frame index")

    syncnet_confidence: float = Field(
        default=0.0, ge=0.0, le=1.0,
        description="Average SyncNet confidence for this phoneme window",
    )


class WordEntry(PhonemeySyncBase):
    """A word with its child phonemes — groups the timeline."""

    word: str
    word_start_ms: int = Field(..., ge=0)
    word_end_ms: int = Field(..., ge=0)
    phonemes: list[PhonemeEntry] = Field(default_factory=list)


class VisemeSummaryEntry(PhonemeySyncBase):
    """Aggregate stats for a single viseme class across the whole audio."""

    count: int = Field(..., ge=0, description="Number of phonemes in this class")
    avg_confidence: float = Field(default=0.0, ge=0.0, le=1.0)


class PhonemesResponse(PhonemeySyncBase):
    """Response to GET /phonemes/{job_id} — the innovation endpoint."""

    job_id: str
    audio_duration_ms: int = Field(..., ge=0)
    total_phonemes: int = Field(..., ge=0)
    timeline: list[WordEntry] = Field(default_factory=list)
    viseme_summary: dict[str, VisemeSummaryEntry] = Field(
        default_factory=dict,
        description="Per-viseme-class aggregate stats",
    )


# ── Error Response ────────────────────────────────────────────────────────────

class ErrorResponse(PhonemeySyncBase):
    """Standard error envelope returned on 4xx/5xx responses."""

    error: str = Field(..., description="Machine-readable error code")
    message: str = Field(..., description="Human-readable error description")
    job_id: Optional[str] = None


# ── Health Check ──────────────────────────────────────────────────────────────

class HealthResponse(PhonemeySyncBase):
    """Response to GET /health."""

    status: str = "ok"
    app_env: str
    device: str
    models_loaded: bool
    redis_connected: bool
