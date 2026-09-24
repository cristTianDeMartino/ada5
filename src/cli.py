"""CLI interface for Customer Search.

Per ARCHITECTURE.md § Interfaces (CLI, NFR-02):
- Usage: python -m src.cli <query>
- Thin adapter: delegates all logic to SearchService.
- Outputs results to stdout, errors to stderr.
- Exit code 0 on success, 1 on error.
"""

import os
import sys

from src.exceptions import DataError, ValidationError
from src.service import SearchService


# Resolve data file relative to project root
_DATA_FILE = os.environ.get(
    "CUSTOMER_DATA_FILE",
    os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "customers.json"),
)


def main(args: list[str] | None = None, data_file: str | None = None) -> int:
    """Run the CLI search.

    Args:
        args: Command line arguments (default: sys.argv[1:]).
        data_file: Path to customer data JSON file.

    Returns:
        Exit code: 0 on success, 1 on error.
    """
    if args is None:
        args = sys.argv[1:]

    if not args:
        print("Usage: python -m src.cli <query>", file=sys.stderr)
        return 1

    query = args[0]
    filepath = data_file or _DATA_FILE

    try:
        service = SearchService(filepath)
        results = service.search(query)

        if not results:
            print("No customers found.")
        else:
            print(f"Found {len(results)} customer(s):")
            for c in results:
                print(f"  [{c.id}] {c.name} — {c.email}")

        return 0

    except ValidationError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    except DataError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
