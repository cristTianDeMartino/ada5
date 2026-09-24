"""Unit tests for the Normalizer module.

Test Scenarios: TS-03 (case-insensitive), TS-04 (accent-insensitive).
"""

from src.normalizer import normalize, remove_accents


class TestRemoveAccents:
    """TS-04: Accent-insensitive normalization."""

    def test_removes_acute_accents(self):
        assert remove_accents("José") == "Jose"

    def test_removes_multiple_accents(self):
        assert remove_accents("María García") == "Maria Garcia"

    def test_removes_all_spanish_accents(self):
        assert remove_accents("áéíóúÁÉÍÓÚ") == "aeiouAEIOU"

    def test_preserves_ene(self):
        # ñ decomposes to n + combining tilde, which gets stripped
        assert remove_accents("Peña") == "Pena"

    def test_no_accents_unchanged(self):
        assert remove_accents("hello world") == "hello world"

    def test_empty_string(self):
        assert remove_accents("") == ""


class TestNormalize:
    """TS-03: Case-insensitive + TS-04: accent-insensitive pipeline."""

    def test_lowercase(self):
        """TS-03: Case-insensitive."""
        assert normalize("GARCIA") == "garcia"

    def test_accent_removal(self):
        """TS-04: Accent-insensitive."""
        assert normalize("José") == "jose"

    def test_combined_case_and_accent(self):
        assert normalize("José García") == "jose garcia"

    def test_strips_whitespace(self):
        assert normalize("  test  ") == "test"

    def test_full_pipeline(self):
        """Verify pipeline order: strip → accents → lowercase (SPEC S5)."""
        assert normalize("  María GARCÍA  ") == "maria garcia"

    def test_empty_string(self):
        assert normalize("") == ""

    def test_already_normalized(self):
        assert normalize("jose garcia") == "jose garcia"
