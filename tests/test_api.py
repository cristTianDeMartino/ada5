"""Integration tests for the HTTP API.

Test Scenarios: TS-11 (200 with results), TS-12 (400 on invalid query).
"""

import json
import threading
import time
import urllib.request
import urllib.error

import pytest

from src.api import create_server


@pytest.fixture(scope="module")
def sample_data_file(tmp_path_factory):
    """Create a temporary JSON file with sample customer data."""
    data = [
        {"id": "c001", "name": "María García", "email": "maria.garcia@example.com"},
        {"id": "c002", "name": "José López", "email": "jose.lopez@example.com"},
    ]
    filepath = tmp_path_factory.mktemp("data") / "customers.json"
    filepath.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    return str(filepath)


@pytest.fixture(scope="module")
def api_server(sample_data_file):
    """Start the HTTP API server in a background thread."""
    server = create_server(host="127.0.0.1", port=0, data_file=sample_data_file)
    port = server.server_address[1]
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    time.sleep(0.3)  # Wait for server to start
    yield f"http://127.0.0.1:{port}"
    server.shutdown()


class TestAPISuccess:
    """TS-11: GET /customers/search?q=mar → 200 with JSON results."""

    def test_search_returns_200_with_results(self, api_server):
        url = f"{api_server}/customers/search?q=mar"
        with urllib.request.urlopen(url) as response:
            assert response.status == 200
            data = json.loads(response.read().decode("utf-8"))
            assert data["count"] >= 1
            assert len(data["results"]) == data["count"]
            assert all("id" in r and "name" in r and "email" in r for r in data["results"])

    def test_search_jose_accent_insensitive(self, api_server):
        url = f"{api_server}/customers/search?q=jose"
        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read().decode("utf-8"))
            assert data["count"] == 1
            assert data["results"][0]["name"] == "José López"

    def test_no_results_returns_200_empty(self, api_server):
        url = f"{api_server}/customers/search?q=zzzznotexist"
        with urllib.request.urlopen(url) as response:
            assert response.status == 200
            data = json.loads(response.read().decode("utf-8"))
            assert data["count"] == 0
            assert data["results"] == []


class TestAPIValidationErrors:
    """TS-12: GET /customers/search?q= → 400 with error JSON."""

    def test_empty_query_returns_400(self, api_server):
        url = f"{api_server}/customers/search?q="
        with pytest.raises(urllib.error.HTTPError) as exc_info:
            urllib.request.urlopen(url)
        assert exc_info.value.code == 400
        data = json.loads(exc_info.value.read().decode("utf-8"))
        assert "error" in data
        assert "empty" in data["error"].lower()

    def test_missing_q_param_returns_400(self, api_server):
        url = f"{api_server}/customers/search"
        with pytest.raises(urllib.error.HTTPError) as exc_info:
            urllib.request.urlopen(url)
        assert exc_info.value.code == 400


class TestAPINotFound:
    """Unknown routes return 404."""

    def test_unknown_path_returns_404(self, api_server):
        url = f"{api_server}/unknown"
        with pytest.raises(urllib.error.HTTPError) as exc_info:
            urllib.request.urlopen(url)
        assert exc_info.value.code == 404

class TestAPIServerErrors:
    """Cover 500 errors (DataError and unexpected Exceptions)."""

    def test_data_error_returns_500(self, api_server):
        # We can force a DataError by requesting an endpoint that makes the service fail,
        # or we can mock the service. Let's monkeypatch the service in the handler.
        url = f"{api_server}/customers/search?q=test"
        
        # This is an integration test, but to force a 500 cleanly we can mock.
        # Instead, let's just make a new server with a bad file.
        server = create_server(host="127.0.0.1", port=0, data_file="/nonexistent/file.json")
        port = server.server_address[1]
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        time.sleep(0.3)
        
        try:
            bad_url = f"http://127.0.0.1:{port}/customers/search?q=test"
            with pytest.raises(urllib.error.HTTPError) as exc_info:
                urllib.request.urlopen(bad_url)
            assert exc_info.value.code == 500
            data = json.loads(exc_info.value.read().decode("utf-8"))
            assert "error" in data
            assert "not found" in data["error"].lower()
        finally:
            server.shutdown()

class TestAPIMain:
    """Test the API entry point (main)."""

    def test_main_starts_server(self, monkeypatch):
        import sys
        from src.api import main
        
        # Mock sys.argv
        monkeypatch.setattr(sys, "argv", ["api.py", "8001"])
        
        # Mock create_server to return a dummy server
        class DummyServer:
            def serve_forever(self):
                pass
            def server_close(self):
                pass
        
        def mock_create_server(host="", port=8000, data_file=None):
            assert port == 8001
            return DummyServer()
            
        monkeypatch.setattr("src.api.create_server", mock_create_server)
        
        # Should not raise any errors
        main()

    def test_main_handles_keyboard_interrupt(self, monkeypatch):
        import sys
        from src.api import main
        
        monkeypatch.setattr(sys, "argv", ["api.py"])
        
        class DummyServer:
            def serve_forever(self):
                raise KeyboardInterrupt()
            def server_close(self):
                self.closed = True
                
        server_instance = DummyServer()
        def mock_create_server(host="", port=8000, data_file=None):
            return server_instance
            
        monkeypatch.setattr("src.api.create_server", mock_create_server)
        
        main()
        assert server_instance.closed
