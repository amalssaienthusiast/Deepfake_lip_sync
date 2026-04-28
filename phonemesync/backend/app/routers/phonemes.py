"""GET /phonemes/{job_id} — the innovation endpoint."""
from __future__ import annotations

import structlog
from fastapi import APIRouter, HTTPException

from app.dependencies import get_job_store
from app.schemas import JobStatus, PhonemesResponse

logger = structlog.get_logger(__name__)
router = APIRouter()


@router.get(
    "/phonemes/{job_id}",
    response_model=PhonemesResponse,
    summary="Fetch phoneme-to-viseme timeline",
)
async def get_phonemes(job_id: str) -> PhonemesResponse:
    """Return the full phoneme timeline for the PhonemeSync Visualizer.

    Each word contains child phonemes with:
    - viseme_class + viseme_color (for canvas rendering)
    - start_ms / end_ms (for timeline positioning)
    - frame_start / frame_end (for video synchronisation)
    - syncnet_confidence (for block height in the visualizer)

    Only available when status === 'done'.
    """
    store = get_job_store()
    job   = store.get_job(job_id)

    if job.status == JobStatus.failed:
        raise HTTPException(
            status_code=400,
            detail=f"Job '{job_id}' failed: {job.error}",
        )

    if job.status != JobStatus.done:
        raise HTTPException(
            status_code=409,
            detail=f"Job '{job_id}' is still {job.status.value}. "
                   "Retry when status is 'done'.",
        )

    phonemes = store.get_phonemes(job_id)
    if phonemes is None:
        raise HTTPException(
            status_code=500,
            detail="Phoneme data not found for completed job.",
        )

    return PhonemesResponse(**phonemes)
