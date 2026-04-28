"""Redis-backed job lifecycle manager.

All job state lives in Redis. Keys:
  phonemesync:job:{job_id}:meta    → JobStatusResponse JSON
  phonemesync:job:{job_id}:result  → ResultResponse JSON
  phonemesync:job:{job_id}:phonemes → PhonemesResponse JSON

All keys use TTL from config.JOB_TTL_SECONDS.
"""
from __future__ import annotations

import json
from datetime import datetime
from typing import Any

import redis
import structlog

from app.config import settings
from app.exceptions import JobNotFoundError
from app.schemas import JobStatus, JobStatusResponse, ProcessingStage

logger = structlog.get_logger(__name__)

_KEY_META     = "phonemesync:job:{job_id}:meta"
_KEY_RESULT   = "phonemesync:job:{job_id}:result"
_KEY_PHONEMES = "phonemesync:job:{job_id}:phonemes"


def _meta_key(job_id: str) -> str:
    return _KEY_META.format(job_id=job_id)

def _result_key(job_id: str) -> str:
    return _KEY_RESULT.format(job_id=job_id)

def _phonemes_key(job_id: str) -> str:
    return _KEY_PHONEMES.format(job_id=job_id)


class JobStore:
    """CRUD operations for async job state in Redis."""

    def __init__(self, client: redis.Redis) -> None:
        self._r = client
        self._ttl = settings.job_ttl_seconds

    # ── Create ────────────────────────────────────────────────────────────────

    def create_job(self, job_id: str, estimated_seconds: int = 45) -> JobStatusResponse:
        """Initialise a new job entry in Redis."""
        now = datetime.utcnow()
        meta = JobStatusResponse(
            job_id=job_id,
            status=JobStatus.queued,
            progress=0,
            stage=None,
            error=None,
            created_at=now,
            updated_at=now,
        )
        self._r.setex(
            name=_meta_key(job_id),
            time=self._ttl,
            value=meta.model_dump_json(),
        )
        logger.info("job_created", job_id=job_id)
        return meta

    # ── Update ────────────────────────────────────────────────────────────────

    def update_status(
        self,
        job_id: str,
        status: JobStatus,
        stage: ProcessingStage | None,
        progress: int,
        error: str | None = None,
    ) -> None:
        """Update job status, stage, and progress atomically."""
        existing = self._get_meta_raw(job_id)
        if existing is None:
            logger.warning("update_status_missing_job", job_id=job_id)
            return

        existing["status"]     = status.value if isinstance(status, JobStatus) else status
        existing["stage"]      = stage.value if isinstance(stage, ProcessingStage) else stage
        existing["progress"]   = progress
        existing["error"]      = error
        existing["updated_at"] = datetime.utcnow().isoformat()

        self._r.setex(
            name=_meta_key(job_id),
            time=self._ttl,
            value=json.dumps(existing),
        )
        logger.info("job_status_updated",
                    job_id=job_id, status=status, stage=stage, progress=progress)

    # ── Read ──────────────────────────────────────────────────────────────────

    def get_job(self, job_id: str) -> JobStatusResponse:
        """Return current job status or raise JobNotFoundError."""
        raw = self._get_meta_raw(job_id)
        if raw is None:
            raise JobNotFoundError(f"Job '{job_id}' not found.")
        return JobStatusResponse(**raw)

    def store_result(self, job_id: str, result_dict: dict[str, Any]) -> None:
        """Persist the full result payload."""
        self._r.setex(
            name=_result_key(job_id),
            time=self._ttl,
            value=json.dumps(result_dict, default=str),
        )
        logger.info("result_stored", job_id=job_id)

    def get_result(self, job_id: str) -> dict[str, Any] | None:
        """Return result dict or None if not yet available."""
        raw = self._r.get(_result_key(job_id))
        return json.loads(raw) if raw else None

    def store_phonemes(self, job_id: str, phonemes_dict: dict[str, Any]) -> None:
        """Persist the phoneme timeline payload."""
        self._r.setex(
            name=_phonemes_key(job_id),
            time=self._ttl,
            value=json.dumps(phonemes_dict, default=str),
        )
        logger.info("phonemes_stored", job_id=job_id)

    def get_phonemes(self, job_id: str) -> dict[str, Any] | None:
        """Return phonemes dict or None if not yet available."""
        raw = self._r.get(_phonemes_key(job_id))
        return json.loads(raw) if raw else None

    # ── Delete ────────────────────────────────────────────────────────────────

    def cleanup_job(self, job_id: str) -> None:
        """Delete all Redis keys for this job (meta + result + phonemes)."""
        keys = [_meta_key(job_id), _result_key(job_id), _phonemes_key(job_id)]
        deleted = self._r.delete(*keys)
        logger.info("job_cleaned_up", job_id=job_id, keys_deleted=deleted)

    # ── Internal ──────────────────────────────────────────────────────────────

    def _get_meta_raw(self, job_id: str) -> dict[str, Any] | None:
        raw = self._r.get(_meta_key(job_id))
        return json.loads(raw) if raw else None
