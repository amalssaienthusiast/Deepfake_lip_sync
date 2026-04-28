"""Application configuration via Pydantic Settings.

All environment variable loading is centralised here.
Import `settings` from this module — never read os.environ directly.
"""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import AnyUrl, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Typed, validated settings loaded from .env / environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Application ──────────────────────────────────────────────────────────
    app_env: Literal["development", "production"] = "development"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"

    # ── Redis ─────────────────────────────────────────────────────────────────
    redis_url: str = "redis://localhost:6379/0"
    job_ttl_seconds: int = Field(default=3600, ge=60)

    # ── Storage ───────────────────────────────────────────────────────────────
    storage_backend: Literal["local"] = "local"
    upload_dir: Path = Path("./tmp/uploads")
    output_dir: Path = Path("./tmp/outputs")
    max_upload_size_mb: int = Field(default=100, ge=1, le=2000)

    # ── ML Models ─────────────────────────────────────────────────────────────
    wav2lip_weights: Path = Path("./app/ml/weights/wav2lip_gan.pth")
    face_detector_weights: Path = Path("./app/ml/weights/s3fd.pth")
    whisper_model_size: Literal["tiny", "base", "small", "medium", "large"] = "base"
    device: Literal["cpu", "cuda"] = "cpu"

    # ── Performance ───────────────────────────────────────────────────────────
    wav2lip_batch_size: int = Field(default=128, ge=1)
    inference_timeout_seconds: int = Field(default=300, ge=30)

    # ── CORS ──────────────────────────────────────────────────────────────────
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:3001"]

    # ── Computed properties ───────────────────────────────────────────────────
    @property
    def max_upload_size_bytes(self) -> int:
        return self.max_upload_size_mb * 1024 * 1024

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"

    @property
    def wav2lip_src_dir(self) -> Path:
        """Absolute path to the cloned Wav2Lip source directory."""
        return Path(__file__).parent / "ml" / "wav2lip_src"

    # ── Validators ───────────────────────────────────────────────────────────
    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: str | list[str]) -> list[str]:
        """Accept a comma-separated string or a list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    @field_validator("upload_dir", "output_dir", mode="after")
    @classmethod
    def ensure_dirs_exist(cls, v: Path) -> Path:
        """Create directories if they don't exist at settings load time."""
        v.mkdir(parents=True, exist_ok=True)
        return v


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return a cached Settings singleton.

    Use this as a FastAPI dependency:
        settings: Settings = Depends(get_settings)
    Or import directly:
        from app.config import settings
    """
    return Settings()


# Module-level singleton for direct import
settings: Settings = get_settings()
