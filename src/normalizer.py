"""Text normalization utilities for search.

Per SPEC.md § Search Rules S3–S5 and ARCHITECTURE.md § Components:
- Pure functions, no state.
- Pipeline: strip → remove accents (NFD) → lowercase.
"""

import re
import unicodedata


def remove_accents(text: str) -> str:
    """Remove diacritical marks from text using Unicode NFD normalization.

    Per SPEC S4: "García" → "Garcia", "José" → "Jose".

    Args:
        text: Input text possibly containing accented characters.

    Returns:
        Text with all combining diacritical marks removed.
    """
    # Decompose into base char + combining marks, then strip marks
    nfd = unicodedata.normalize("NFD", text)
    return re.sub(r"[\u0300-\u036f]", "", nfd)


def normalize(text: str) -> str:
    """Normalize text for search comparison.

    Pipeline per SPEC S5: strip → remove accents → lowercase.

    Args:
        text: Input text to normalize.

    Returns:
        Normalized text ready for substring comparison.
    """
    stripped = text.strip()
    without_accents = remove_accents(stripped)
    return without_accents.lower()
