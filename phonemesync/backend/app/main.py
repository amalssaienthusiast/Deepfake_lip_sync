"""FastAPI application entry point for PhonemeSync.

Lifespan: warm up all ML models on startup, clean up on shutdown.
Middleware: CORS, request logging.
Static files: /outputs served directly from disk.
Routers: all 4 endpoint groups under /api/v1.
Health check: GET /health
"""
from __future__ import annotations

import asyncio
import time
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncGenerator

import structlog
import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.exceptions import (
    InferenceTooLongError,
    JobNotFoundError,
    NoFaceDetectedError,
    PhonemeSyncBaseError,
)
from app.routers import phonemes, process, result, status
from app.schemas import ErrorResponse, HealthResponse

# ── Logging setup ─────────────────────────────────────────────────────────────

structlog.configure(
    processors=[
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.dev.ConsoleRenderer()
        if not settings.is_production
        else structlog.processors.JSONRenderer(),
    ],
    wrapper_class=structlog.make_filtering_bound_logger(
        getattr(__import__("logging"), settings.log_level)
    ),
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),
)

logger = structlog.get_logger(__name__)

# ── Model warm-up state ───────────────────────────────────────────────────────

_MODELS_LOADED: bool = False
_REDIS_CONNECTED: bool = False


async def _warmup_models() -> None:
    """Pre-load all ML models into memory at startup.

    This takes ~30 seconds on first run but eliminates per-request
    cold-start latency during the demo.
    """
    global _MODELS_LOADED
    t0 = time.perf_counter()
    logger.info("warming_up_models", whisper_size=settings.whisper_model_size,
                device=settings.device)
    try:
        # Import services here to trigger lazy model loading
        from app.services.wav2lip_svc import Wav2LipService  # noqa: F401
        from app.services.whisper_svc import WhisperService  # noqa: F401
        from app.services.mediapipe_svc import MediaPipeService  # noqa: F401
        from app.services.syncnet_svc import SyncNetService  # noqa: F401

        # Force initialisation (constructors load the models)
        from app.dependencies import (
            get_wav2lip_service,
            get_whisper_service,
            get_mediapipe_service,
            get_syncnet_service,
        )
        get_wav2lip_service()
        get_whisper_service()
        get_mediapipe_service()
        get_syncnet_service()

        elapsed = time.perf_counter() - t0
        _MODELS_LOADED = True
        logger.info("models_loaded", elapsed_seconds=round(elapsed, 2))
    except Exception as exc:
        logger.error("model_warmup_failed", error=str(exc))
        # Don't crash the server — let it start and fail gracefully on requests
        _MODELS_LOADED = False


async def _check_redis() -> None:
    """Verify Redis is reachable on startup."""
    global _REDIS_CONNECTED
    try:
        from app.dependencies import get_redis_client
        client = get_redis_client()
        await asyncio.to_thread(client.ping)
        _REDIS_CONNECTED = True
        logger.info("redis_connected", url=settings.redis_url)
    except Exception as exc:
        _REDIS_CONNECTED = False
        logger.warning("redis_connection_failed", error=str(exc))


# ── Lifespan ──────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Manage application startup and shutdown lifecycle."""
    # Ensure storage directories exist
    settings.upload_dir.mkdir(parents=True, exist_ok=True)
    settings.output_dir.mkdir(parents=True, exist_ok=True)
    logger.info("storage_dirs_ready",
                upload=str(settings.upload_dir),
                output=str(settings.output_dir))

    # Run checks concurrently
    await asyncio.gather(
        _check_redis(),
        _warmup_models(),
    )

    logger.info("phonemesync_api_ready",
                env=settings.app_env,
                device=settings.device,
                models_loaded=_MODELS_LOADED,
                redis=_REDIS_CONNECTED)

    yield  # ← application runs here

    logger.info("phonemesync_api_shutting_down")


# ── App factory ───────────────────────────────────────────────────────────────

def create_app() -> FastAPI:
    """Construct and configure the FastAPI application."""
    app = FastAPI(
        title="PhonemeSync API",
        description=(
            "Audio-driven lip synthesis with phoneme-level sync confidence. "
            "IBM Project · 24hr Sprint · Wav2Lip + Whisper + SyncNet."
        ),
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # ── CORS ──────────────────────────────────────────────────────────────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Static file serving ───────────────────────────────────────────────────
    settings.output_dir.mkdir(parents=True, exist_ok=True)
    app.mount(
        "/outputs",
        StaticFiles(directory=str(settings.output_dir)),
        name="outputs",
    )

    # ── Routers ───────────────────────────────────────────────────────────────
    prefix = "/api/v1"
    app.include_router(process.router,  prefix=prefix, tags=["Process"])
    app.include_router(status.router,   prefix=prefix, tags=["Status"])
    app.include_router(result.router,   prefix=prefix, tags=["Result"])
    app.include_router(phonemes.router, prefix=prefix, tags=["Phonemes"])

    # ── Health check ──────────────────────────────────────────────────────────
    @app.get("/health", response_model=HealthResponse, summary="Health check")
    async def health() -> HealthResponse:
        return HealthResponse(
            status="ok",
            app_env=settings.app_env,
            device=settings.device,
            models_loaded=_MODELS_LOADED,
            redis_connected=_REDIS_CONNECTED,
        )

    # ── Global exception handlers ─────────────────────────────────────────────

    @app.exception_handler(NoFaceDetectedError)
    async def no_face_handler(request: Request, exc: NoFaceDetectedError) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content=ErrorResponse(
                error="no_face_detected",
                message=exc.message,
            ).model_dump(),
        )

    @app.exception_handler(InferenceTooLongError)
    async def too_long_handler(request: Request, exc: InferenceTooLongError) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content=ErrorResponse(
                error="inference_too_long",
                message=exc.message,
            ).model_dump(),
        )

    @app.exception_handler(JobNotFoundError)
    async def not_found_handler(request: Request, exc: JobNotFoundError) -> JSONResponse:
        return JSONResponse(
            status_code=404,
            content=ErrorResponse(
                error="job_not_found",
                message=exc.message,
            ).model_dump(),
        )

    @app.exception_handler(PhonemeSyncBaseError)
    async def base_error_handler(request: Request, exc: PhonemeSyncBaseError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content=ErrorResponse(
                error=type(exc).__name__,
                message=exc.message,
            ).model_dump(),
        )

    return app


# ── Application instance ──────────────────────────────────────────────────────

app = create_app()

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=not settings.is_production,
        log_level=settings.log_level.lower(),
    )
