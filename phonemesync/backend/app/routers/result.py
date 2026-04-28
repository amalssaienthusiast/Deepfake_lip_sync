"""GET /result/{job_id} — fetch synthesis result after job completes."""
from __future__ import annotations

import structlog
from fastapi import APIRouter, HTTPException

from app.dependencies import get_job_store
from app.exceptions import JobNotFoundError
from app.schemas import JobStatus, ResultResponse

logger = structlog.get_logger(__name__)
router = APIRouter()


@router.get(
    "/result/{job_id}",
    response_model=ResultResponse,
    summary="Fetch synthesis result",
)
async def get_result(job_id: str) -> ResultResponse:
    """Return the full synthesis result for a completed job.

    Only available when status === 'done'.
    Returns 404 if job not found, 409 if job is still processing.
    """
    store = get_job_store()
    job   = store.get_job(job_id)   # raises 404 if not found

    if job.status == JobStatus.failed:
        raise HTTPException(
            status_code=400,
            detail=f"Job '{job_id}' failed: {job.error}",
        )

    if job.status != JobStatus.done:
        raise HTTPException(
            status_code=409,
            detail=f"Job '{job_id}' is still {job.status.value}. "
                   "Poll /status/{job_id} and retry when done.",
        )

    result = store.get_result(job_id)
    if result is None:
        raise HTTPException(
            status_code=500,
            detail=f"Job '{job_id}' is marked done but result is missing.",
        )

    return ResultResponse(**result)
