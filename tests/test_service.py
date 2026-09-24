"""Unit tests for the SearchService.

Test Scenarios: TS-01 (partial name), TS-02 (partial email),
TS-03 (case-insensitive), TS-04 (accent-insensitive),
TS-05 (simultaneous name+email), TS-06 (no results).
"""

import json
import os
import tempfile

import pytest

from src.exceptions import DataError, ValidationError
from src.service import SearchService


@pytest.fixture
def sample_data_file(tmp_path):
    """Create a temporary JSON file with sample customer data."""
    data = [
        {"id": "c001", "name": "María García", "email": "maria.garcia@example.com"},
        {"id": "c002", "name": "José López", "email": "jose.lopez@example.com"},
        {"id": "c003", "name": "Ana Martínez", "email": "ana.martinez@example.com"},
        {"id": "c004", "name": "Carlos Hernández", "email": "carlos.hernandez@correo.mx"},
        {"id": "c005", "name": "Marcos García", "email": "marcos.garcia@example.com"},
    ]
    filepath = tmp_path / "customers.json"
    filepath.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    return str(filepath)


@pytest.fixture
def service(sample_data_file):
    """Create a SearchService with sample data."""
    return SearchService(sample_data_file)


class TestPartialNameSearch:
    """TS-01: Partial search by name."""

    def test_partial_name_mar(self, service):
        """Query 'mar' matches 'María', 'Marcos' by name."""
        results = service.search("mar")
        names = [c.name for c in results]
        assert "María García" in names
        assert "Marcos García" in names

    def test_partial_name_ana(self, service):
        results = service.search("ana")
        names = [c.name for c in results]
        assert "Ana Martínez" in names


class TestPartialEmailSearch:
    """TS-02: Partial search by email."""

    def test_partial_email_domain(self, service):
        """Query '@example' matches all @example.com emails."""
        results = service.search("@example")
        assert all("@example.com" in c.email for c in results)
        assert len(results) == 4  # c001, c002, c003, c005

    def test_partial_email_correo(self, service):
        results = service.search("correo.mx")
        assert len(results) == 1
        assert results[0].name == "Carlos Hernández"


class TestCaseInsensitive:
    """TS-03: Case-insensitive search."""

    def test_uppercase_query(self, service):
        results = service.search("GARCIA")
        names = [c.name for c in results]
        assert "María García" in names
        assert "Marcos García" in names

    def test_mixed_case_query(self, service):
        results = service.search("JoSe")
        assert len(results) == 1
        assert results[0].name == "José López"


class TestAccentInsensitive:
    """TS-04: Accent-insensitive search."""

    def test_no_accent_matches_accented(self, service):
        """'jose' matches 'José'."""
        results = service.search("jose")
        assert any(c.name == "José López" for c in results)

    def test_accented_query_matches(self, service):
        """'García' matches 'García'."""
        results = service.search("García")
        names = [c.name for c in results]
        assert "María García" in names

    def test_martinez_without_accent(self, service):
        results = service.search("martinez")
        assert any(c.name == "Ana Martínez" for c in results)


class TestSimultaneousSearch:
    """TS-05: Search matches name AND email simultaneously."""

    def test_garcia_matches_name_and_email(self, service):
        """'garcia' appears in name ('García') and email ('garcia@...')."""
        results = service.search("garcia")
        assert len(results) >= 2  # At least María and Marcos García
        # Verify we get results from both name and email matches
        ids = [c.id for c in results]
        assert "c001" in ids  # María García (name match)
        assert "c005" in ids  # Marcos García (name + email match)


class TestNoResults:
    """TS-06: No matches returns empty list."""

    def test_no_match_returns_empty(self, service):
        results = service.search("zzzznotexist")
        assert results == []

    def test_returns_list_type(self, service):
        results = service.search("zzzznotexist")
        assert isinstance(results, list)


class TestOriginalValues:
    """Verify results contain original (non-normalized) values (FR-06, SPEC S6)."""

    def test_results_have_original_accents(self, service):
        results = service.search("jose")
        assert results[0].name == "José López"  # Original, not "jose lopez"

    def test_results_have_original_email(self, service):
        results = service.search("jose")
        assert results[0].email == "jose.lopez@example.com"


class TestDataError:
    """Repository errors propagate correctly."""

    def test_missing_file_raises_data_error(self):
        service = SearchService("/nonexistent/path.json")
        with pytest.raises(DataError, match="Customer data file not found"):
            service.search("test")

    def test_invalid_json_raises_data_error(self, tmp_path):
        bad_file = tmp_path / "bad.json"
        bad_file.write_text("{invalid json", encoding="utf-8")
        service = SearchService(str(bad_file))
        with pytest.raises(DataError, match="Invalid JSON"):
            service.search("test")
