"""HTTP API for Customer Search.

Per ARCHITECTURE.md § Interfaces (HTTP API, NFR-02):
- GET /customers/search?q=<query> → 200 with results or 400/500 with error.
- Thin adapter: delegates all logic to SearchService.
- Uses stdlib http.server (DD-2: zero external dependencies).
"""

import json
import os
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

from src.exceptions import DataError, ValidationError
from src.service import SearchService


# Resolve data file relative to project root
_DATA_FILE = os.environ.get(
    "CUSTOMER_DATA_FILE",
    os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "customers.json"),
)


class CustomerSearchHandler(BaseHTTPRequestHandler):
    """HTTP request handler for customer search."""

    service: SearchService  # Set by the server factory

    def do_GET(self) -> None:
        """Handle GET requests."""
        parsed = urlparse(self.path)

        if parsed.path == "/customers/search":
            self._handle_search(parsed)
        else:
            self._send_json(404, {"error": "Not found"})

    def _handle_search(self, parsed) -> None:
        """Handle GET /customers/search?q=<query>."""
        params = parse_qs(parsed.query)
        query = params.get("q", [""])[0]

        try:
            results = self.service.search(query)
            response = {
                "results": [
                    {"id": c.id, "name": c.name, "email": c.email} for c in results
                ],
                "count": len(results),
            }
            self._send_json(200, response)

        except ValidationError as e:
            self._send_json(400, {"error": str(e)})

        except DataError as e:
            self._send_json(500, {"error": str(e)})

        except Exception:
            self._send_json(500, {"error": "Internal server error"})

    def _send_json(self, status: int, data: dict) -> None:
        """Send a JSON response."""
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        """Suppress default request logging during tests."""
        pass


def create_server(host: str = "", port: int = 8000, data_file: str | None = None) -> HTTPServer:
    """Create and return an HTTP server instance.

    Args:
        host: Bind address (empty string = all interfaces).
        port: Port number (default 8000, NFR-02).
        data_file: Path to customer data JSON file.

    Returns:
        Configured HTTPServer ready to serve.
    """
    filepath = data_file or _DATA_FILE
    service = SearchService(filepath)

    # Attach service to handler class
    handler = type(
        "Handler",
        (CustomerSearchHandler,),
        {"service": service},
    )

    return HTTPServer((host, port), handler)


def main() -> None:
    """Run the HTTP API server."""
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    server = create_server(port=port)
    print(f"Customer Search API running on http://localhost:{port}")
    print("Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down.")
        server.server_close()


if __name__ == "__main__":
    main()
