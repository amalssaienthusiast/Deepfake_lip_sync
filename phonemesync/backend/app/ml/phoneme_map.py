"""CMU Phoneme → 12-class Viseme Mapping.

This is the core lookup table that powers the PhonemeSync innovation layer.
Every CMU/ARPAbet phoneme symbol maps to exactly one of 12 viseme classes,
each with a distinct hex color for the timeline visualizer.

Source: CMU Pronouncing Dictionary (ARPAbet) + standard viseme taxonomy.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class VisemeInfo:
    """Immutable viseme class descriptor."""

    cls: str          # snake_case class name
    label: str        # human-readable label for UI display
    color: str        # hex color for canvas rendering
    description: str  # mouth shape description for documentation


# ── 12 Viseme Class Definitions ──────────────────────────────────────────────

VISEME_CLASSES: dict[str, VisemeInfo] = {
    "silence": VisemeInfo(
        cls="silence",
        label="Silence / Pause",
        color="#94A3B8",
        description="Mouth closed, no active articulation",
    ),
    "bilabial": VisemeInfo(
        cls="bilabial",
        label="Bilabial",
        color="#EC4899",
        description="Both lips pressed together (p, b, m sounds)",
    ),
    "labiodental": VisemeInfo(
        cls="labiodental",
        label="Labiodental",
        color="#F97316",
        description="Upper teeth touching lower lip (f, v sounds)",
    ),
    "dental": VisemeInfo(
        cls="dental",
        label="Dental",
        color="#EAB308",
        description="Tongue between or near teeth (th sounds)",
    ),
    "alveolar": VisemeInfo(
        cls="alveolar",
        label="Alveolar",
        color="#22C55E",
        description="Tongue tip at alveolar ridge (t, d, n, l sounds)",
    ),
    "postalveolar": VisemeInfo(
        cls="postalveolar",
        label="Post-alveolar",
        color="#14B8A6",
        description="Tongue behind alveolar ridge (sh, zh, ch, j sounds)",
    ),
    "velar": VisemeInfo(
        cls="velar",
        label="Velar",
        color="#6366F1",
        description="Back of tongue at soft palate (k, g, ng sounds)",
    ),
    "glottal": VisemeInfo(
        cls="glottal",
        label="Glottal",
        color="#8B5CF6",
        description="Constriction at glottis (h sound)",
    ),
    "front_vowel": VisemeInfo(
        cls="front_vowel",
        label="Front Vowel",
        color="#3B82F6",
        description="High front tongue position (ee, ih, eh, ae sounds)",
    ),
    "mid_vowel": VisemeInfo(
        cls="mid_vowel",
        label="Mid Vowel",
        color="#F97316",
        description="Mid/central tongue position (uh, er sounds)",
    ),
    "back_vowel": VisemeInfo(
        cls="back_vowel",
        label="Back Vowel",
        color="#EF4444",
        description="High back/rounded tongue position (aa, aw, oh, oo sounds)",
    ),
    "diphthong": VisemeInfo(
        cls="diphthong",
        label="Diphthong",
        color="#10B981",
        description="Gliding vowel movement (ow, igh, oy, ay sounds)",
    ),
}


# ── Full ARPAbet → Viseme Mapping ────────────────────────────────────────────
# Every CMU phoneme symbol mapped to a viseme class key.
# Stress markers (0, 1, 2) are stripped before lookup.

PHONEME_TO_VISEME: dict[str, str] = {
    # ── Silence / Boundary ──
    "SIL": "silence",
    "SP":  "silence",
    "SPN": "silence",

    # ── Bilabial stops + nasal ──
    "P":  "bilabial",
    "B":  "bilabial",
    "M":  "bilabial",
    "EM": "bilabial",   # syllabic m

    # ── Labiodental fricatives ──
    "F": "labiodental",
    "V": "labiodental",

    # ── Dental fricatives ──
    "TH": "dental",
    "DH": "dental",

    # ── Alveolar stops, nasal, lateral ──
    "T":  "alveolar",
    "D":  "alveolar",
    "N":  "alveolar",
    "L":  "alveolar",
    "EN": "alveolar",   # syllabic n
    "EL": "alveolar",   # syllabic l

    # ── Sibilant fricatives / affricates (post-alveolar) ──
    "S":  "alveolar",    # alveolar sibilant
    "Z":  "alveolar",    # alveolar sibilant
    "SH": "postalveolar",
    "ZH": "postalveolar",
    "CH": "postalveolar",
    "JH": "postalveolar",

    # ── Retroflex / Rhotic ──
    "R": "alveolar",    # approximant, lip shape close to alveolar

    # ── Palatal approximant ──
    "Y": "front_vowel",

    # ── Velar stops + nasal ──
    "K":  "velar",
    "G":  "velar",
    "NG": "velar",
    "ENG": "velar",   # syllabic ng

    # ── Glottal fricative ──
    "HH": "glottal",

    # ── Labiovelar approximant ──
    "W": "bilabial",   # rounded, lip shape similar to bilabial

    # ── Front vowels ──
    "IY": "front_vowel",   # fleece
    "IH": "front_vowel",   # kit
    "EH": "front_vowel",   # dress
    "AE": "front_vowel",   # trap

    # ── Mid / Central vowels ──
    "AH": "mid_vowel",    # strut / schwa
    "AX": "mid_vowel",    # schwa (alternative symbol)
    "ER": "mid_vowel",    # nurse
    "AXR": "mid_vowel",   # schwa + r

    # ── Back vowels ──
    "AA": "back_vowel",   # lot / palm
    "AO": "back_vowel",   # thought
    "OW": "back_vowel",   # goat (some analyses treat as diphthong)
    "UH": "back_vowel",   # foot
    "UW": "back_vowel",   # goose

    # ── Diphthongs ──
    "AW": "diphthong",   # mouth
    "AY": "diphthong",   # price
    "OY": "diphthong",   # choice
    "EY": "diphthong",   # face
}

# Fallback for any phoneme not in the dict above
_FALLBACK_VISEME = "mid_vowel"


def phoneme_to_viseme(phoneme_symbol: str) -> VisemeInfo:
    """Resolve a CMU phoneme symbol to its VisemeInfo.

    Strips stress markers (trailing 0/1/2) before lookup.
    Falls back to mid_vowel for unknown symbols.

    Args:
        phoneme_symbol: ARPAbet phoneme string, e.g. "AH1", "P", "SH".

    Returns:
        VisemeInfo for the closest matching viseme class.
    """
    # Strip numeric stress markers
    clean = phoneme_symbol.rstrip("012").upper()
    viseme_cls = PHONEME_TO_VISEME.get(clean, _FALLBACK_VISEME)
    return VISEME_CLASSES[viseme_cls]


def get_viseme_color(phoneme_symbol: str) -> str:
    """Return the hex color string for a phoneme symbol."""
    return phoneme_to_viseme(phoneme_symbol).color


def get_viseme_class(phoneme_symbol: str) -> str:
    """Return the viseme class string for a phoneme symbol."""
    return phoneme_to_viseme(phoneme_symbol).cls


# ── Convenience export: all class names ──────────────────────────────────────
ALL_VISEME_CLASSES: list[str] = list(VISEME_CLASSES.keys())
