"""In-memory job store for local development without Redis.

This is a fallback implementation that stores job state in memory.
Used when Redis is unavailable.
"""
from __future__ import annotations

import json
from datetime import datetime
from typing import Any, Optional

import structlog

from app.config import settings
from app.exceptions import JobNotFoundError
from app.schemas import JobStatus, JobStatusResponse, ProcessingStage

logger = structlog.get_logger(__name__)


class InMemoryJobStore:
    """Simple in-memory job state store for development/testing.
    
    ⚠️ NOTE: State is lost on server restart. For production, use Redis.
    """

    def __init__(self) -> None:
        self._jobs: dict[str, dict[str, Any]] = {}
        self._ttl = settings.job_ttl_seconds

    def create_job(self, job_id: str, estimated_seconds: int = 45) -> JobStatusResponse:
        """Initialize a new job entry."""
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
        self._jobs[job_id] = {
            "meta": meta.model_dump(mode="json"),
            "result": None,
            "phonemes": None,
        }
        logger.info("job_created", job_id=job_id, store="memory")
        return meta

    def update_status(
        self,
        job_id: str,
        status: JobStatus,
        stage: Optional[ProcessingStage],
        progress: int,
        error: Optional[str] = None,
    ) -> None:
        """Update job status and progress."""
        if job_id not in self._jobs:
            raise JobNotFoundError(job_id)

        now = datetime.utcnow()
        existing = self._jobs[job_id]["meta"]
        existing["status"] = status.value
        existing["stage"] = stage.value if stage else None
        existing["progress"] = progress
        existing["error"] = error
        existing["updated_at"] = now.isoformat()
        logger.info("job_updated", job_id=job_id, status=status, progress=progress)

    def get_status(self, job_id: str) -> JobStatusResponse:
        """Retrieve job status."""
        if job_id not in self._jobs:
            raise JobNotFoundError(job_id)
        
        data = self._jobs[job_id]["meta"]
        return JobStatusResponse(
            job_id=data["job_id"],
            status=JobStatus(data["status"]),
            progress=data["progress"],
            stage=ProcessingStage(data["stage"]) if data["stage"] else None,
            error=data["error"],
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
        )

    def get_job(self, job_id: str) -> JobStatusResponse:
        """Compatibility alias used by the status router."""
        return self.get_status(job_id)

    def store_result(self, job_id: str, result_dict: dict[str, Any]) -> None:
        """Store synthesis result."""
        if job_id not in self._jobs:
            raise JobNotFoundError(job_id)
        self._jobs[job_id]["result"] = result_dict
        logger.info("result_stored", job_id=job_id)

    def get_result(self, job_id: str) -> Optional[dict[str, Any]]:
        """Retrieve result or None if not ready."""
        if job_id not in self._jobs:
            raise JobNotFoundError(job_id)
        return self._jobs[job_id]["result"]

    def store_phonemes(self, job_id: str, phonemes_dict: dict[str, Any]) -> None:
        """Store phoneme timeline."""
        if job_id not in self._jobs:
            raise JobNotFoundError(job_id)
        self._jobs[job_id]["phonemes"] = phonemes_dict
        logger.info("phonemes_stored", job_id=job_id)

    def get_phonemes(self, job_id: str) -> Optional[dict[str, Any]]:
        """Retrieve phonemes or None if not ready."""
        if job_id not in self._jobs:
            raise JobNotFoundError(job_id)
        return self._jobs[job_id]["phonemes"]

    def cleanup_job(self, job_id: str) -> None:
        """Remove job (usually on expiry)."""
        self._jobs.pop(job_id, None)
        logger.info("job_cleaned", job_id=job_id)
