"""GET /status/{job_id} — poll job progress."""
from __future__ import annotations

import structlog
from fastapi import APIRouter

from app.dependencies import get_job_store
from app.schemas import JobStatusResponse

logger = structlog.get_logger(__name__)
router = APIRouter()


@router.get(
    "/status/{job_id}",
    response_model=JobStatusResponse,
    summary="Poll job processing status",
)
async def get_status(job_id: str) -> JobStatusResponse:
    """Return current status and progress for a queued/running job.

    Raises 404 (JobNotFoundError) if job_id is unknown or expired.
    Frontend should poll every 2 seconds while status is queued|processing.
    """
    store = get_job_store()
    return store.get_job(job_id)   # raises JobNotFoundError → 404 via handler
