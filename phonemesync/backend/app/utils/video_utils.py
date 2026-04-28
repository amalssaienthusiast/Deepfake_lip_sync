"""Video utilities — FFmpeg probing and conversion wrappers."""
from __future__ import annotations

from pathlib import Path
from typing import Any

import structlog

logger = structlog.get_logger(__name__)


def probe_video(path: Path) -> dict[str, Any]:
    """Return FFmpeg probe dict for a video/audio file."""
    import ffmpeg
    try:
        return ffmpeg.probe(str(path))
    except Exception as exc:
        logger.error("ffmpeg_probe_failed", path=str(path), error=str(exc))
        return {}


def get_duration(path: Path) -> float:
    probe = probe_video(path)
    try:
        return float(probe["format"]["duration"])
    except (KeyError, TypeError, ValueError):
        return 0.0


def get_fps(path: Path) -> float:
    probe = probe_video(path)
    try:
        for stream in probe.get("streams", []):
            if stream.get("codec_type") == "video":
                r = stream.get("r_frame_rate", "25/1")
                num, den = r.split("/")
                return float(num) / float(den)
    except Exception:
        pass
    return 25.0


def extract_audio(video_path: Path, output_wav: Path) -> Path:
    """Extract audio track from video as 16kHz mono WAV."""
    import ffmpeg
    output_wav.parent.mkdir(parents=True, exist_ok=True)
    (
        ffmpeg
        .input(str(video_path))
        .output(str(output_wav), ar=16000, ac=1, acodec="pcm_s16le")
        .overwrite_output()
        .run(quiet=True)
    )
    return output_wav
