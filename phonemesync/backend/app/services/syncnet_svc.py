"""SyncNet per-frame confidence scoring service.

Uses Wav2Lip's discriminator as a confidence proxy.
Spec: Section 7.4
"""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

import cv2
import numpy as np
import structlog

from app.config import settings

logger = structlog.get_logger(__name__)


class SyncNetService:
    """Scores per-frame audio-visual synchronization confidence."""

    def __init__(self) -> None:
        wav2lip_str = str(settings.wav2lip_src_dir)
        if wav2lip_str not in sys.path:
            sys.path.insert(0, wav2lip_str)
        self._disc = None
        self._load_discriminator()

    def _load_discriminator(self) -> None:
        try:
            import torch
            from models import SyncNet_color as SyncNet

            ckpt = torch.load(
                str(settings.wav2lip_weights), map_location=settings.device
            )
            # SyncNet lives inside the Wav2Lip checkpoint as "disc_state_dict"
            disc_state = ckpt.get("disc_state_dict", None)
            if disc_state is None:
                logger.warning("syncnet_disc_not_in_checkpoint_using_proxy")
                return

            model = SyncNet()
            model.load_state_dict(disc_state)
            model = model.to(settings.device)
            model.eval()
            self._disc = model
            logger.info("syncnet_discriminator_loaded")
        except Exception as exc:
            logger.warning("syncnet_load_failed_using_proxy", error=str(exc))
            self._disc = None

    async def score_video(
        self, video_path: Path, audio_path: Path
    ) -> list[float]:
        return await asyncio.to_thread(
            self._score_sync, video_path, audio_path
        )

    def _score_sync(self, video_path: Path, audio_path: Path) -> list[float]:
        """Return per-frame confidence scores in [0, 1]."""
        cap = cv2.VideoCapture(str(video_path))
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
        cap.release()

        if frame_count == 0:
            return []

        if self._disc is None:
            # Proxy: use motion-based heuristic
            return self._proxy_scores(video_path, frame_count)

        try:
            return self._disc_scores(video_path, audio_path, frame_count, fps)
        except Exception as exc:
            logger.warning("syncnet_inference_failed_using_proxy", error=str(exc))
            return self._proxy_scores(video_path, frame_count)

    def _proxy_scores(
        self, video_path: Path, frame_count: int
    ) -> list[float]:
        """Optical-flow proxy: frames with more lip motion get higher score."""
        cap   = cv2.VideoCapture(str(video_path))
        scores: list[float] = []
        prev_gray = None

        while True:
            ok, frame = cap.read()
            if not ok:
                break
            h, w = frame.shape[:2]
            # Crop lip region (lower third of frame)
            lip = frame[int(h * 0.55):int(h * 0.85), int(w * 0.25):int(w * 0.75)]
            gray = cv2.cvtColor(lip, cv2.COLOR_BGR2GRAY)

            if prev_gray is None:
                scores.append(0.5)
            else:
                diff  = cv2.absdiff(gray, prev_gray).astype(float)
                score = float(np.clip(diff.mean() / 30.0, 0.0, 1.0))
                scores.append(round(0.4 + score * 0.5, 4))

            prev_gray = gray
        cap.release()

        # Smooth with a simple moving average (window=3)
        smoothed: list[float] = []
        for i in range(len(scores)):
            window = scores[max(0, i - 1):i + 2]
            smoothed.append(round(sum(window) / len(window), 4))
        return smoothed

    def _disc_scores(
        self,
        video_path: Path,
        audio_path: Path,
        frame_count: int,
        fps: float,
    ) -> list[float]:
        import torch
        from audio import load_wav, melspectrogram  # wav2lip_src

        wav = load_wav(str(audio_path), 16000)
        mel = melspectrogram(wav)
        mel_step = 16
        scores: list[float] = []

        cap = cv2.VideoCapture(str(video_path))
        idx = 0
        while True:
            ok, frame = cap.read()
            if not ok:
                break

            h, w = frame.shape[:2]
            lip = cv2.resize(
                frame[int(h * 0.55):int(h * 0.85), int(w * 0.25):int(w * 0.75)],
                (48, 48),
            )
            img_t = (
                torch.FloatTensor(lip.transpose(2, 0, 1) / 255.0)
                .unsqueeze(0)
                .to(settings.device)
            )

            mel_i = int(idx * 80.0 / fps)
            mel_chunk = mel[:, mel_i:mel_i + mel_step]
            if mel_chunk.shape[1] < mel_step:
                mel_chunk = np.pad(
                    mel_chunk, ((0, 0), (0, mel_step - mel_chunk.shape[1]))
                )
            mel_t = (
                torch.FloatTensor(mel_chunk[np.newaxis, np.newaxis, :, :])
                .to(settings.device)
            )

            with torch.no_grad():
                _, conf = self._disc(mel_t, img_t)
                score = float(torch.sigmoid(conf).cpu().item())

            scores.append(round(score, 4))
            idx += 1

        cap.release()
        return scores
