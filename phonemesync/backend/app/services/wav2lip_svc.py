"""Wav2Lip inference service wrapper.

Wraps the Wav2Lip GAN model for lip-sync synthesis.
Uses subprocess to isolate the heavy inference environment.
"""
from __future__ import annotations

import asyncio
import shutil
import cv2 #type:ignore
from pathlib import Path
from typing import Any

import structlog #type:ignore

from app.config import settings
from app.exceptions import NoFaceDetectedError, PhonemeSyncBaseError

logger = structlog.get_logger(__name__)


class Wav2LipService:
    """Service to run Wav2Lip inference."""

    def __init__(self) -> None:
        self.wav2lip_dir = settings.wav2lip_src_dir
        self.weights_path = settings.wav2lip_weights
        # Wav2Lip writes intermediate files to a `temp/` subdir.
        # It MUST be writable by the container user — create it here.
        self.temp_dir = self.wav2lip_dir / "temp"
        self.temp_dir.mkdir(parents=True, exist_ok=True)

        if not self.weights_path.exists():
            logger.warning("wav2lip_weights_missing", path=str(self.weights_path))

    async def run_inference(self, face_path: Path, audio_path: Path, output_path: Path) -> dict[str, Any]:
        """Run the Wav2Lip inference pipeline."""
        logger.info("wav2lip_starting", face=str(face_path), audio=str(audio_path))

        if not self.weights_path.exists():
            raise PhonemeSyncBaseError(
                message=f"Wav2Lip weights not found at {self.weights_path}. Download wav2lip_gan.pth and place it in app/ml/weights/."
            )

        cmd = [
            "python", "-u", "inference.py",
            "--checkpoint_path", str(self.weights_path),
            "--face", str(face_path),
            "--audio", str(audio_path),
            "--outfile", str(output_path),
            "--face_det_batch_size", "4",
            "--wav2lip_batch_size", "32",
        ]

        # Merge stderr into stdout so we never lose crash output
        process = await asyncio.create_subprocess_exec(
            *cmd,
            cwd=str(self.wav2lip_dir),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
            env={
                **__import__('os').environ,
                "PYTHONUNBUFFERED": "1",
            },
        )

        stdout, _ = await process.communicate()
        output_text = stdout.decode(errors="replace")

        if process.returncode != 0:
            logger.error("wav2lip_failed", output=output_text[-500:], code=process.returncode)
            if "Face not detected" in output_text:
                raise NoFaceDetectedError("Wav2Lip could not detect a face in the input video.")
            raise PhonemeSyncBaseError(
                message=f"Wav2Lip failed (exit {process.returncode}): {output_text[-300:]}"
            )

        logger.info("wav2lip_stdout", tail=output_text[-200:])

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
