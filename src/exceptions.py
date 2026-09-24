"""Custom exceptions for the Customer Search application.

Defined per ARCHITECTURE.md § Error Handling:
- ValidationError: raised when input validation fails (FR-08, FR-09, FR-10).
- DataError: raised when customer data cannot be loaded (e.g., file not found).
"""


class ValidationError(Exception):
    """Raised when the search query fails validation rules (V1, V2)."""
    pass


class DataError(Exception):
    """Raised when the customer data source is unavailable or corrupt."""
    pass
