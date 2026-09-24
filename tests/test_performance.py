"""Performance test for customer search.

Test Scenario: TS-10 — 1,000 records, search ≤ 200 ms (NFR-01).
"""

import json
import time
import uuid

import pytest

from src.service import SearchService


@pytest.fixture(scope="module")
def large_data_file(tmp_path_factory):
    """Generate a JSON file with 1,000 customer records."""
    data = []
    for i in range(1000):
        data.append(
            {
                "id": str(uuid.uuid4()),
                "name": f"Customer {i} García López",
                "email": f"customer{i}@example.com",
            }
        )
    filepath = tmp_path_factory.mktemp("perf") / "customers.json"
    filepath.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    return str(filepath)


class TestPerformance:
    """TS-10: Performance with 1,000 records."""

    def test_search_1000_records_under_200ms(self, large_data_file):
        """Search over 1,000 records must complete in ≤ 200 ms (NFR-01)."""
        service = SearchService(large_data_file)

        # Warm up cache
        service.search("warmup")

        # Measure search time
        start = time.perf_counter()
        results = service.search("garcia")
        elapsed_ms = (time.perf_counter() - start) * 1000

        assert elapsed_ms <= 200, f"Search took {elapsed_ms:.1f} ms (limit: 200 ms)"
        assert len(results) == 1000  # All records have "García" in the name

    def test_search_no_match_1000_records_under_200ms(self, large_data_file):
        """Even with no matches, search must be fast."""
        service = SearchService(large_data_file)
        service.search("warmup")

        start = time.perf_counter()
        results = service.search("zzzznotexist")
        elapsed_ms = (time.perf_counter() - start) * 1000

        assert elapsed_ms <= 200, f"Search took {elapsed_ms:.1f} ms (limit: 200 ms)"
        assert len(results) == 0
