"""Custom exception classes for PhonemeSync.

All application-level exceptions live here.
Never raise generic Exception in service code — use one of these.
"""
from __future__ import annotations


class PhonemeSyncBaseError(Exception):
    """Base class for all PhonemeSync errors."""

    message: str = "An unexpected error occurred."
    status_code: int = 500

    def __init__(self, message: str | None = None) -> None:
        self.message = message or self.__class__.message
        super().__init__(self.message)


class NoFaceDetectedError(PhonemeSyncBaseError):
    """Raised when no face is found in the uploaded image/video."""

    message = "Could not detect a face in the uploaded image/video."
    status_code = 422


class InferenceTooLongError(PhonemeSyncBaseError):
    """Raised when audio/video exceeds the prototype duration limit."""

    message = "Input duration exceeds the 60-second limit for this prototype."
    status_code = 422


class JobNotFoundError(PhonemeSyncBaseError):
    """Raised when a job_id does not exist in the Redis store."""

    message = "Job not found. It may have expired or the ID is incorrect."
    status_code = 404


class InvalidFileTypeError(PhonemeSyncBaseError):
    """Raised when an uploaded file has an unsupported MIME/extension."""

    message = "Unsupported file type. Check allowed formats and try again."
    status_code = 422


class AudioProcessingError(PhonemeSyncBaseError):
    """Raised when audio preprocessing (resample, convert) fails."""

    message = "Failed to process the audio file."
    status_code = 422


class StorageError(PhonemeSyncBaseError):
    """Raised when reading or writing files to disk fails."""

    message = "A storage error occurred."
    status_code = 500
