"""Pytest configuration and shared fixtures."""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture(scope="session")
def client() -> TestClient:
    """FastAPI test client — reused across the test session."""
    with TestClient(app) as c:
        yield c


@pytest.fixture
def sample_image(tmp_path):
    """Generate a tiny 96x96 black JPEG for face input tests."""
    import cv2
    import numpy as np
    img  = np.zeros((96, 96, 3), dtype=np.uint8)
    path = tmp_path / "test_face.jpg"
    cv2.imwrite(str(path), img)
    return path


@pytest.fixture
def sample_audio(tmp_path):
    """Generate a 1-second silent WAV for audio input tests."""
    import numpy as np
    import soundfile as sf
    data = np.zeros(16000, dtype=np.float32)
    path = tmp_path / "test_audio.wav"
    sf.write(str(path), data, 16000)
    return path
