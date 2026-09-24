"""Unit tests for the Validator module.

Test Scenarios: TS-07 (empty query), TS-08 (spaces only), TS-09 (double spaces).
"""

import pytest

from src.exceptions import ValidationError
from src.validator import validate_query


class TestValidateQueryEmpty:
    """TS-07: Empty query → error."""

    def test_empty_string_raises(self):
        with pytest.raises(ValidationError, match="Query must not be empty"):
            validate_query("")

    def test_returns_trimmed_valid_query(self):
        assert validate_query("jose") == "jose"

    def test_returns_trimmed_query_with_leading_space(self):
        assert validate_query("  jose  ") == "jose"


class TestValidateQuerySpacesOnly:
    """TS-08: Spaces-only query → error."""

    def test_single_space_raises(self):
        with pytest.raises(ValidationError, match="Query must not be empty"):
            validate_query(" ")

    def test_multiple_spaces_raises(self):
        with pytest.raises(ValidationError, match="Query must not be empty"):
            validate_query("     ")

    def test_tabs_and_spaces_raises(self):
        with pytest.raises(ValidationError, match="Query must not be empty"):
            validate_query("\t  \t")


class TestValidateQueryConsecutiveSpaces:
    """TS-09: Double space → error."""

    def test_double_space_raises(self):
        with pytest.raises(
            ValidationError, match="Query must not contain consecutive spaces"
        ):
            validate_query("Ana  García")

    def test_triple_space_raises(self):
        with pytest.raises(
            ValidationError, match="Query must not contain consecutive spaces"
        ):
            validate_query("test   email")

    def test_single_space_valid(self):
        result = validate_query("Ana García")
        assert result == "Ana García"

    def test_multiple_words_single_spaces_valid(self):
        result = validate_query("Ana María García")
        assert result == "Ana María García"
