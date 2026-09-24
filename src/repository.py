"""Customer data repository.

Loads customer data from a JSON file and caches it in memory.
Per ARCHITECTURE.md § Components: reads and caches data, knows nothing
about search or validation.
"""

import json
from pathlib import Path

from src.exceptions import DataError
from src.models import Customer


class CustomerRepository:
    """Loads and caches customer records from a JSON file."""

    def __init__(self, filepath: str) -> None:
        self._filepath = filepath
        self._cache: list[Customer] | None = None

    def load(self) -> list[Customer]:
        """Load customers from JSON. Caches after first read.

        Returns:
            list[Customer]: All customer records.

        Raises:
            DataError: If the data file is not found or contains invalid JSON.
        """
        if self._cache is not None:
            return self._cache

        path = Path(self._filepath)
        if not path.exists():
            raise DataError("Customer data file not found")

        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            raise DataError(f"Invalid JSON in customer data file: {e}") from e

        self._cache = [
            Customer(id=record["id"], name=record["name"], email=record["email"])
            for record in data
        ]
        return self._cache
