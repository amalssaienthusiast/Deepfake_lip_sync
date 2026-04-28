"""POST /process — submit a lip-sync job."""
from __future__ import annotations

import asyncio
import uuid
from pathlib import Path

import structlog
from fastapi import APIRouter, BackgroundTasks, File, HTTPException, UploadFile

from app.config import settings
from app.dependencies import get_job_store
from app.exceptions import InvalidFileTypeError, NoFaceDetectedError
from app.schemas import ErrorResponse, JobSubmitResponse
from app.workers.inference_worker import run_pipeline

logger = structlog.get_logger(__name__)
router = APIRouter()

_ALLOWED_VIDEO = {".mp4", ".avi", ".mov", ".webm"}
_ALLOWED_IMAGE = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
_ALLOWED_AUDIO = {".wav", ".mp3", ".aac", ".m4a", ".ogg"}
_ALLOWED_FACE  = _ALLOWED_VIDEO | _ALLOWED_IMAGE


def _check_ext(filename: str, allowed: set[str], field: str) -> str:
    suffix = Path(filename).suffix.lower()
    if suffix not in allowed:
        raise InvalidFileTypeError(
            f"'{field}' has unsupported extension '{suffix}'. "
            f"Allowed: {sorted(allowed)}"
        )
    return suffix


async def _save_upload(upload: UploadFile, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    content = await upload.read()
    if len(content) > settings.max_upload_size_bytes:
        raise HTTPException(
            status_code=422,
            detail=f"File '{upload.filename}' exceeds "
                   f"{settings.max_upload_size_mb} MB limit.",
        )
    dest.write_bytes(content)


@router.post(
    "/process",
    response_model=JobSubmitResponse,
    status_code=202,
    summary="Submit a lip-sync job",
)
async def submit_process(
    background_tasks: BackgroundTasks,
    video_file: UploadFile = File(..., description="Face source image or video"),
    audio_file: UploadFile = File(..., description="Target speech audio"),
) -> JobSubmitResponse:
    """Accept face + audio, validate file types, queue async job.

    Returns immediately with job_id. Poll /status/{job_id} for progress.
    """
    job_id = str(uuid.uuid4())
    job_dir = settings.upload_dir / job_id
    job_dir.mkdir(parents=True, exist_ok=True)

    # Validate extensions
    face_ext  = _check_ext(video_file.filename or "", _ALLOWED_FACE,  "video_file")
    audio_ext = _check_ext(audio_file.filename or "", _ALLOWED_AUDIO, "audio_file")

    face_path  = job_dir / f"face{face_ext}"
    audio_path = job_dir / f"audio{audio_ext}"

    await _save_upload(video_file, face_path)
    await _save_upload(audio_file, audio_path)

    # Create Redis job entry
    store = get_job_store()
    response = store.create_job(job_id)

    # Fire-and-forget background pipeline
    background_tasks.add_task(run_pipeline, job_id, face_path, audio_path)

    logger.info("job_queued", job_id=job_id,
                face=face_path.name, audio=audio_path.name)

    return JobSubmitResponse(
        job_id=job_id,
        status=response.status,
        estimated_seconds=45,
        created_at=response.created_at,
    )
