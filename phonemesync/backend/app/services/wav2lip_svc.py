"""Wav2Lip inference service wrapper.

Wraps the Wav2Lip GAN model for lip-sync synthesis.
Uses subprocess to isolate the heavy inference environment.
"""
from __future__ import annotations

import asyncio
import os
import cv2
from pathlib import Path
from typing import Any

import structlog

from app.config import settings
from app.exceptions import InferenceTooLongError, NoFaceDetectedError, PhonemeSyncBaseError

logger = structlog.get_logger(__name__)


class Wav2LipService:
    """Service to run Wav2Lip inference."""

    def __init__(self) -> None:
        self.wav2lip_dir = settings.wav2lip_src_dir
        self.weights_path = settings.wav2lip_weights
        self.temp_dir = self.wav2lip_dir / "temp"
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        
        if not self.weights_path.exists():
            logger.warning("wav2lip_weights_missing", path=str(self.weights_path))

    async def run_inference(self, face_path: Path, audio_path: Path, output_path: Path) -> dict[str, Any]:
        """Run the Wav2Lip inference pipeline."""
        logger.info("wav2lip_starting", face=str(face_path), audio=str(audio_path))

        # Check audio length (for InferenceTooLongError)
        # Using a simple check if possible, or assume it's valid.

        cmd = [
            "python", "inference.py",
            "--checkpoint_path", str(self.weights_path),
            "--face", str(face_path),
            "--audio", str(audio_path),
            "--outfile", str(output_path),
            "--face_det_batch_size", "8",
            "--wav2lip_batch_size", str(settings.wav2lip_batch_size),
        ]
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            cwd=str(self.wav2lip_dir),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            err_output = stderr.decode()
            logger.error("wav2lip_failed", stderr=err_output)
            if "Face not detected" in err_output:
                raise NoFaceDetectedError("Wav2Lip could not detect a face in the input video.")
            raise PhonemeSyncBaseError(
                message=f"Wav2Lip inference failed: {err_output[-200:]}"
            )

        # Get video properties
        fps = 25.0
        duration_seconds = 0.0
        try:
            cap = cv2.VideoCapture(str(output_path))
            if cap.isOpened():
                fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
                frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
                if fps > 0:
                    duration_seconds = frame_count / fps
            cap.release()
        except Exception as e:
            logger.warning("failed_to_probe_video", error=str(e))

        logger.info("wav2lip_complete", output=str(output_path), fps=fps, duration=duration_seconds)
        
        return {
            "fps": fps,
            "duration_seconds": duration_seconds,
        }
