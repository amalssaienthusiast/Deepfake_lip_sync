"""Dependency injection providers for PhonemeSync.

All singletons (Redis client, ML services) are instantiated once here
and injected into routers/workers via FastAPI's Depends() or direct import.
"""
from __future__ import annotations

from functools import lru_cache

import redis as redis_lib

from app.config import settings


# ── Redis ─────────────────────────────────────────────────────────────────────

@lru_cache(maxsize=1)
def get_redis_client() -> redis_lib.Redis:
    """Return a cached Redis client (connection pool under the hood)."""
    return redis_lib.from_url(
        settings.redis_url,
        decode_responses=True,
        socket_connect_timeout=5,
        socket_timeout=5,
    )


# ── ML Service singletons ─────────────────────────────────────────────────────
# Services are imported lazily to avoid importing heavy ML libraries
# (torch, whisper, mediapipe) until they are actually needed.

@lru_cache(maxsize=1)
def get_wav2lip_service():  # type: ignore[return]
    from app.services.wav2lip_svc import Wav2LipService
    return Wav2LipService()


@lru_cache(maxsize=1)
def get_whisper_service():  # type: ignore[return]
    from app.services.whisper_svc import WhisperService
    return WhisperService()


@lru_cache(maxsize=1)
def get_syncnet_service():  # type: ignore[return]
    from app.services.syncnet_svc import SyncNetService
    return SyncNetService()


@lru_cache(maxsize=1)
def get_mediapipe_service():  # type: ignore[return]
    from app.services.mediapipe_svc import MediaPipeService
    return MediaPipeService()


@lru_cache(maxsize=1)
def get_job_store():  # type: ignore[return]
    from app.services.job_store import JobStore
    return JobStore(client=get_redis_client())
