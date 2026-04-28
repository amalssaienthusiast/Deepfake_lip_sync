"""Tests for GET /phonemes/{job_id} — Sprint 3 DoD."""
from __future__ import annotations

from app.ml.phoneme_map import ALL_VISEME_CLASSES, get_viseme_class


def test_all_viseme_classes_defined():
    assert len(ALL_VISEME_CLASSES) == 12


def test_phoneme_to_viseme_known_symbols():
    assert get_viseme_class("P")   == "bilabial"
    assert get_viseme_class("B")   == "bilabial"
    assert get_viseme_class("M")   == "bilabial"
    assert get_viseme_class("F")   == "labiodental"
    assert get_viseme_class("V")   == "labiodental"
    assert get_viseme_class("SH")  == "postalveolar"
    assert get_viseme_class("HH")  == "glottal"
    assert get_viseme_class("IY")  == "front_vowel"
    assert get_viseme_class("AH")  == "mid_vowel"
    assert get_viseme_class("AY")  == "diphthong"
    assert get_viseme_class("SIL") == "silence"


def test_stress_markers_stripped():
    assert get_viseme_class("AH0") == get_viseme_class("AH")
    assert get_viseme_class("IY1") == get_viseme_class("IY")
    assert get_viseme_class("OW2") == get_viseme_class("OW")


def test_unknown_phoneme_falls_back():
    result = get_viseme_class("XYZ_UNKNOWN")
    assert result in ALL_VISEME_CLASSES   # must return a valid class


def test_phoneme_response_schema():
    """Validate a hand-crafted phoneme response parses correctly."""
    from app.schemas import PhonemesResponse, VisemeClass

    data = {
        "job_id": "test-job",
        "audio_duration_ms": 3000,
        "total_phonemes": 4,
        "timeline": [
            {
                "word": "hello",
                "word_start_ms": 0,
                "word_end_ms": 480,
                "phonemes": [
                    {
                        "symbol": "HH",
                        "viseme_class": "glottal",
                        "viseme_color": "#8B5CF6",
                        "start_ms": 0,
                        "end_ms": 120,
                        "frame_start": 0,
                        "frame_end": 3,
                        "syncnet_confidence": 0.75,
                    }
                ],
            }
        ],
        "viseme_summary": {},
    }
    resp = PhonemesResponse(**data)
    assert resp.total_phonemes == 4
    ph = resp.timeline[0].phonemes[0]
    assert 0.0 <= ph.syncnet_confidence <= 1.0
    assert ph.viseme_class in [v.value for v in VisemeClass]
