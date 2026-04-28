"""Audio utilities — resampling, mono conversion, format validation."""
from __future__ import annotations

from pathlib import Path

import structlog

logger = structlog.get_logger(__name__)

_TARGET_SR  = 16000   # Hz — Wav2Lip and Whisper both expect 16kHz
_TARGET_CH  = 1       # mono


def to_wav_16k_mono(src: Path, dst: Path) -> Path:
    """Convert any audio file to 16kHz mono WAV.

    Uses FFmpeg under the hood — handles mp3, aac, m4a, ogg, etc.
    """
    import ffmpeg
    dst.parent.mkdir(parents=True, exist_ok=True)
    (
        ffmpeg
        .input(str(src))
        .output(str(dst), ar=_TARGET_SR, ac=_TARGET_CH, acodec="pcm_s16le")
        .overwrite_output()
        .run(quiet=True)
    )
    logger.info("audio_converted", src=src.name, dst=dst.name)
    return dst


def get_sample_rate(path: Path) -> int:
    """Return sample rate of an audio file."""
    import soundfile as sf
    try:
        info = sf.info(str(path))
        return info.samplerate
    except Exception:
        return 0


def validate_audio(path: Path) -> bool:
    """Return True if the file is a readable audio file."""
    try:
        import soundfile as sf
        with sf.SoundFile(str(path)):
            return True
    except Exception:
        # Fall back to FFmpeg probe
        try:
            import ffmpeg
            probe = ffmpeg.probe(str(path))
            return any(
                s.get("codec_type") == "audio"
                for s in probe.get("streams", [])
            )
        except Exception:
            return False
