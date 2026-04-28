"""Async pipeline orchestrator — runs all 4 ML stages in sequence.

Spec: Section 7.6
"""
from __future__ import annotations

import asyncio
import statistics
import time
from pathlib import Path
from typing import Any

import structlog

from app.config import settings
from app.schemas import JobStatus, ProcessingStage

logger = structlog.get_logger(__name__)


async def run_pipeline(job_id: str, face_path: Path, audio_path: Path) -> None:
    """Orchestrate the full PhonemeSync ML pipeline for one job.

    Stages:
        wav2lip   → 0–40%
        whisper   → 40–60%
        syncnet   → 60–80%
        mediapipe → 80–95%
        assemble  → 95–100%
    """
    from app.dependencies import (
        get_job_store,
        get_mediapipe_service,
        get_syncnet_service,
        get_wav2lip_service,
        get_whisper_service,
    )

    store      = get_job_store()
    wav2lip    = get_wav2lip_service()
    whisper    = get_whisper_service()
    syncnet    = get_syncnet_service()
    mediapipe  = get_mediapipe_service()

    output_dir = settings.output_dir / job_id
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path  = output_dir / "synced.mp4"
    t_start      = time.perf_counter()
    wav2lip_result: dict[str, Any] = {}

    try:
        # ── Stage 1: Wav2Lip ──────────────────────────────────────────────────
        store.update_status(job_id, JobStatus.processing, ProcessingStage.wav2lip, 0)
        wav2lip_result = await wav2lip.run_inference(face_path, audio_path, output_path)
        store.update_status(job_id, JobStatus.processing, ProcessingStage.wav2lip, 40)

        fps = wav2lip_result.get("fps", 25.0)

        # Copy original face as "original" for side-by-side player
        import shutil
        orig_dest = output_dir / "original.mp4"
        if face_path.suffix.lower() in {".mp4", ".avi", ".mov"}:
            shutil.copy2(face_path, orig_dest)
        else:
            # Convert image to 1-second video
            _image_to_video(face_path, orig_dest, fps)

        # ── Stage 2: Whisper ──────────────────────────────────────────────────
        store.update_status(job_id, JobStatus.processing, ProcessingStage.whisper, 40)
        timeline = await whisper.extract_phoneme_timeline(audio_path, fps)
        store.update_status(job_id, JobStatus.processing, ProcessingStage.whisper, 60)

        # ── Stage 3: SyncNet ──────────────────────────────────────────────────
        store.update_status(job_id, JobStatus.processing, ProcessingStage.syncnet, 60)
        syncnet_scores = await syncnet.score_video(output_path, audio_path)
        store.update_status(job_id, JobStatus.processing, ProcessingStage.syncnet, 80)

        # ── Stage 4: MediaPipe ────────────────────────────────────────────────
        store.update_status(job_id, JobStatus.processing, ProcessingStage.mediapipe, 80)
        lip_landmarks = await mediapipe.extract_lip_landmarks(output_path)
        store.update_status(job_id, JobStatus.processing, ProcessingStage.mediapipe, 95)

        # ── Stage 5: Assemble + store ─────────────────────────────────────────
        elapsed = time.perf_counter() - t_start

        # Attach syncnet confidence to each phoneme entry
        timeline = _attach_syncnet_to_phonemes(timeline, syncnet_scores, fps)

        # Build viseme summary
        viseme_summary = _build_viseme_summary(timeline)

        # Count total phonemes
        total_phonemes = sum(len(w["phonemes"]) for w in timeline)

        # Compute audio duration from last word end
        audio_duration_ms = (
            timeline[-1]["word_end_ms"] if timeline else 0
        )

        # Compute SyncNet stats
        avg_conf = statistics.mean(syncnet_scores) if syncnet_scores else 0.0
        std_conf = statistics.stdev(syncnet_scores) if len(syncnet_scores) > 1 else 0.0

        # Build resolution
        import cv2 as _cv2
        cap = _cv2.VideoCapture(str(output_path))
        w_px = int(cap.get(_cv2.CAP_PROP_FRAME_WIDTH))
        h_px = int(cap.get(_cv2.CAP_PROP_FRAME_HEIGHT))
        cap.release()

        result_dict = {
            "job_id":                    job_id,
            "video_url":                 f"/outputs/{job_id}/synced.mp4",
            "original_video_url":        f"/outputs/{job_id}/original.mp4",
            "duration_seconds":          wav2lip_result.get("duration_seconds", 0.0),
            "fps":                       fps,
            "resolution":                [w_px, h_px],
            "syncnet_scores":            syncnet_scores,
            "syncnet_avg":               round(avg_conf, 4),
            "syncnet_std":               round(std_conf, 4),
            "lip_landmarks":             lip_landmarks,
            "processing_time_seconds":   round(elapsed, 2),
            "model_used":                "wav2lip_gan",
        }

        phonemes_dict = {
            "job_id":            job_id,
            "audio_duration_ms": audio_duration_ms,
            "total_phonemes":    total_phonemes,
            "timeline":          timeline,
            "viseme_summary":    viseme_summary,
        }

        store.store_result(job_id, result_dict)
        store.store_phonemes(job_id, phonemes_dict)
        store.update_status(job_id, JobStatus.done, ProcessingStage.done, 100)
        logger.info("pipeline_complete", job_id=job_id, elapsed_s=round(elapsed, 2))

    except Exception as exc:
        logger.error("pipeline_failed", job_id=job_id, error=str(exc), exc_info=True)
        store.update_status(
            job_id, JobStatus.failed, None, 0, error=str(exc)
        )
    finally:
        # Clean up upload files
        for p in [face_path, audio_path]:
            try:
                p.unlink(missing_ok=True)
            except Exception:
                pass


# ── Helpers ───────────────────────────────────────────────────────────────────

def _attach_syncnet_to_phonemes(
    timeline: list[dict],
    syncnet_scores: list[float],
    fps: float,
) -> list[dict]:
    """Attach avg SyncNet confidence to each phoneme entry."""
    for word in timeline:
        for ph in word["phonemes"]:
            fs = ph.get("frame_start", 0)
            fe = ph.get("frame_end", fs)
            window = syncnet_scores[fs:fe + 1]
            ph["syncnet_confidence"] = round(
                statistics.mean(window) if window else 0.0, 4
            )
    return timeline


def _build_viseme_summary(timeline: list[dict]) -> dict:
    """Aggregate per-viseme-class stats."""
    buckets: dict[str, list[float]] = {}
    for word in timeline:
        for ph in word["phonemes"]:
            cls  = ph.get("viseme_class", "mid_vowel")
            conf = ph.get("syncnet_confidence", 0.0)
            buckets.setdefault(cls, []).append(conf)

    summary: dict = {}
    for cls, confs in buckets.items():
        summary[cls] = {
            "count":          len(confs),
            "avg_confidence": round(statistics.mean(confs), 4) if confs else 0.0,
        }
    return summary


def _image_to_video(image_path: Path, output_path: Path, fps: float) -> None:
    """Convert a static image to a 1-second video."""
    import cv2
    img = cv2.imread(str(image_path))
    if img is None:
        return
    h, w = img.shape[:2]
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(str(output_path), fourcc, fps, (w, h))
    for _ in range(int(fps)):
        writer.write(img)
    writer.release()
