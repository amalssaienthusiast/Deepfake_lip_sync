"""Tests for POST /process endpoint — Sprint 1 DoD."""
from __future__ import annotations

import io
import pytest
from fastapi.testclient import TestClient


def test_submit_with_valid_image_and_audio(client, sample_image, sample_audio):
    with open(sample_image, "rb") as img, open(sample_audio, "rb") as aud:
        resp = client.post(
            "/api/v1/process",
            files={
                "video_file": ("face.jpg", img, "image/jpeg"),
                "audio_file": ("audio.wav", aud, "audio/wav"),
            },
        )
    assert resp.status_code == 202
    data = resp.json()
    assert "job_id" in data
    assert data["status"] == "queued"
    assert len(data["job_id"]) == 36   # UUID v4


def test_submit_with_invalid_file_type(client, sample_audio):
    fake_pdf = io.BytesIO(b"%PDF-1.4 fake content")
    with open(sample_audio, "rb") as aud:
        resp = client.post(
            "/api/v1/process",
            files={
                "video_file": ("document.pdf", fake_pdf, "application/pdf"),
                "audio_file": ("audio.wav", aud, "audio/wav"),
            },
        )
    assert resp.status_code == 422


def test_submit_missing_audio(client, sample_image):
    with open(sample_image, "rb") as img:
        resp = client.post(
            "/api/v1/process",
            files={"video_file": ("face.jpg", img, "image/jpeg")},
        )
    assert resp.status_code == 422


def test_status_returns_queued_after_submit(client, sample_image, sample_audio):
    with open(sample_image, "rb") as img, open(sample_audio, "rb") as aud:
        submit = client.post(
            "/api/v1/process",
            files={
                "video_file": ("face.jpg", img, "image/jpeg"),
                "audio_file": ("audio.wav", aud, "audio/wav"),
            },
        )
    job_id = submit.json()["job_id"]
    status_resp = client.get(f"/api/v1/status/{job_id}")
    assert status_resp.status_code == 200
    assert status_resp.json()["status"] in ("queued", "processing", "done")


def test_status_unknown_job_returns_404(client):
    resp = client.get("/api/v1/status/nonexistent-job-id")
    assert resp.status_code == 404
