"""Query validation.

Per SPEC.md § Validation Rules V1–V3:
- V1: Query must not be empty after trimming (FR-08).
- V2: Query must not contain consecutive spaces (FR-09).
- V3: Validation runs server-side in the service layer (FR-10).
"""

import re

from src.exceptions import ValidationError


def validate_query(query: str) -> str:
    """Validate a search query string.

    Args:
        query: The raw query string from the user.

    Returns:
        The trimmed query string if valid.

    Raises:
        ValidationError: If the query is empty or contains consecutive spaces.
    """
    # V1: Must not be empty after trim (FR-08)
    trimmed = query.strip()
    if not trimmed:
        raise ValidationError("Query must not be empty")

    # V2: Must not contain consecutive spaces (FR-09)
    if re.search(r"  +", trimmed):
        raise ValidationError("Query must not contain consecutive spaces")

    return trimmed
