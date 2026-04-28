"""MediaPipe FaceMesh lip landmark extraction service.

Spec: Section 7.5
"""
from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any, Optional

import cv2
import numpy as np
import structlog

logger = structlog.get_logger(__name__)

# MediaPipe lip landmark indices (468-point face mesh)
_LIP_OUTER = [61,146,91,181,84,17,314,405,321,375,291,308,324,318,402,317,14,87,178,88,95]
_LIP_INNER = [78,95,88,178,87,14,317,402,318,324,308]
_PADDING   = 10  # pixels of bounding box padding


class MediaPipeService:
    """Extracts lip landmarks and bounding boxes per video frame."""

    def __init__(self) -> None:
        import mediapipe as mp
        self._face_mesh = mp.solutions.face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
        )
        logger.info("mediapipe_face_mesh_loaded")

    async def extract_lip_landmarks(
        self, video_path: Path
    ) -> list[dict[str, Any]]:
        return await asyncio.to_thread(
            self._extract_sync, video_path
        )

    def _extract_sync(self, video_path: Path) -> list[dict[str, Any]]:
        cap  = cv2.VideoCapture(str(video_path))
        fps  = cap.get(cv2.CAP_PROP_FPS) or 25.0
        results_list: list[dict[str, Any]] = []
        prev_entry: Optional[dict[str, Any]]  = None
        frame_idx = 0

        while True:
            ok, frame = cap.read()
            if not ok:
                break

            h, w = frame.shape[:2]
            rgb   = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_result = self._face_mesh.process(rgb)

            if mp_result.multi_face_landmarks:
                lm = mp_result.multi_face_landmarks[0].landmark

                outer = [
                    [int(lm[i].x * w), int(lm[i].y * h)]
                    for i in _LIP_OUTER
                ]
                inner = [
                    [int(lm[i].x * w), int(lm[i].y * h)]
                    for i in _LIP_INNER
                ]
                all_pts = np.array(outer)
                x0 = max(0, int(all_pts[:, 0].min()) - _PADDING)
                y0 = max(0, int(all_pts[:, 1].min()) - _PADDING)
                x1 = min(w, int(all_pts[:, 0].max()) + _PADDING)
                y1 = min(h, int(all_pts[:, 1].max()) + _PADDING)

                entry: dict[str, Any] = {
                    "frame_idx":    frame_idx,
                    "timestamp_ms": int(frame_idx / fps * 1000),
                    "lip_outer":    outer,
                    "lip_inner":    inner,
                    "lip_bbox":     {"x": x0, "y": y0, "w": x1 - x0, "h": y1 - y0},
                }
                prev_entry = entry
            else:
                # No face detected — reuse previous frame
                if prev_entry is not None:
                    entry = prev_entry.copy()
                    entry["frame_idx"]    = frame_idx
                    entry["timestamp_ms"] = int(frame_idx / fps * 1000)
                else:
                    entry = {
                        "frame_idx":    frame_idx,
                        "timestamp_ms": int(frame_idx / fps * 1000),
                        "lip_outer":    [],
                        "lip_inner":    [],
                        "lip_bbox":     {"x": 0, "y": 0, "w": 0, "h": 0},
                    }

            results_list.append(entry)
            frame_idx += 1

        cap.release()
        logger.info("lip_landmarks_extracted", frames=len(results_list))
        return results_list
