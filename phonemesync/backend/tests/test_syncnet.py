"""Tests for SyncNet scoring — Sprint 3 DoD."""
from __future__ import annotations

import pytest
import numpy as np


def test_proxy_scores_in_range(tmp_path):
    """Proxy optical-flow scorer must return values in [0, 1]."""
    import cv2
    from app.services.syncnet_svc import SyncNetService

    # Create a tiny 10-frame test video
    video_path = tmp_path / "test.mp4"
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    w = cv2.VideoWriter(str(video_path), fourcc, 25, (96, 96))
    for i in range(10):
        frame = np.random.randint(0, 255, (96, 96, 3), dtype=np.uint8)
        w.write(frame)
    w.release()

    svc = SyncNetService()
    # Use proxy directly (no real audio needed)
    scores = svc._proxy_scores(video_path, 10)

    assert len(scores) == 10
    for s in scores:
        assert 0.0 <= s <= 1.0, f"Score {s} out of [0,1] range"


def test_syncnet_scores_length_matches_frames(tmp_path):
    """Score list length must equal frame count."""
    import cv2
    import soundfile as sf
    from app.services.syncnet_svc import SyncNetService

    video_path = tmp_path / "v.mp4"
    audio_path = tmp_path / "a.wav"

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    vw = cv2.VideoWriter(str(video_path), fourcc, 25, (96, 96))
    for _ in range(25):
        vw.write(np.zeros((96, 96, 3), dtype=np.uint8))
    vw.release()

    sf.write(str(audio_path), np.zeros(16000, dtype=np.float32), 16000)

    svc = SyncNetService()
    scores = svc._proxy_scores(video_path, 25)
    assert len(scores) == 25
