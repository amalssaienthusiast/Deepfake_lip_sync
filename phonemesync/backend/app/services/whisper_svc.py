"""Whisper-based phoneme extraction and viseme mapping service.

Spec: Section 7.3
"""
from __future__ import annotations

import asyncio
import math
from pathlib import Path
from typing import Any

import structlog #type:ignore

from app.config import settings
from app.ml.phoneme_map import get_viseme_class, get_viseme_color

logger = structlog.get_logger(__name__)


class WhisperService:
    """Transcribes audio and produces a phoneme-to-viseme timeline."""

    def __init__(self) -> None:
        import nltk #type:ignore
        nltk.download("cmudict", quiet=True)

        import whisper #type:ignore
        self._model = whisper.load_model(settings.whisper_model_size)
        logger.info("whisper_loaded", size=settings.whisper_model_size)

        import pronouncing #type:ignore
        self._pronouncing = pronouncing

    async def extract_phoneme_timeline(
        self, audio_path: Path, fps: float
    ) -> list[dict[str, Any]]:
        return await asyncio.to_thread(
            self._extract_sync, audio_path, fps
        )

    def _extract_sync(self, audio_path: Path, fps: float) -> list[dict[str, Any]]:
        import whisper #type:ignore

        audio = whisper.load_audio(str(audio_path))
        result = self._model.transcribe(
            audio,
            word_timestamps=True,
            language="en",
        )

        words: list[dict[str, Any]] = []
        for seg in result.get("segments", []):
            for w in seg.get("words", []):
                words.append(w)

        timeline: list[dict[str, Any]] = []
        for w in words:
            word_text  = w.get("word", "").strip().lower()
            word_start = int(w.get("start", 0) * 1000)
            word_end   = int(w.get("end", 0) * 1000)

            phones = self._pronouncing.phones_for_word(word_text)
            if phones:
                phoneme_list = phones[0].split()
            else:
                # Fallback: one mid_vowel phoneme for the whole word
                phoneme_list = ["AH"]

            duration = max(word_end - word_start, 1)
            step     = duration / len(phoneme_list)

            phoneme_entries: list[dict[str, Any]] = []
            for i, sym in enumerate(phoneme_list):
                ph_start = word_start + int(i * step)
                ph_end   = word_start + int((i + 1) * step)
                phoneme_entries.append({
                    "symbol":            sym,
                    "viseme_class":      get_viseme_class(sym),
                    "viseme_color":      get_viseme_color(sym),
                    "start_ms":          ph_start,
                    "end_ms":            ph_end,
                    "frame_start":       int(ph_start / 1000 * fps),
                    "frame_end":         int(ph_end   / 1000 * fps),
                    "syncnet_confidence": 0.0,  # filled later by worker
                })

            timeline.append({
                "word":          word_text,
                "word_start_ms": word_start,
                "word_end_ms":   word_end,
                "phonemes":      phoneme_entries,
            })

        logger.info("phoneme_timeline_built", words=len(timeline))
        return timeline
