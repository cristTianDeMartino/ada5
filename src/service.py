"""Customer search service.

Orchestrates: validate → normalize → match → return results.
Per ARCHITECTURE.md § Components: the single source of truth for
search logic. CLI and API delegate to this service.
"""

from src.models import Customer
from src.normalizer import normalize
from src.repository import CustomerRepository
from src.validator import validate_query


class SearchService:
    """Core search service that validates, normalizes, and filters customers."""

    def __init__(self, filepath: str) -> None:
        self._repo = CustomerRepository(filepath)

    def search(self, query: str) -> list[Customer]:
        """Search customers by name or email.

        Per SPEC § Search Rules S1–S7 and Validation Rules V1–V3:
        1. Validate the query (FR-08, FR-09, FR-10).
        2. Normalize the query (FR-03, FR-04).
        3. Match against each customer's name and email (FR-02, FR-05).
        4. Return matching customers with original values (FR-06).
        5. Return empty list if no matches (FR-07).

        Args:
            query: The search string from the user.

        Returns:
            list[Customer]: Matching customer records with original values.

        Raises:
            ValidationError: If the query fails validation (FR-08, FR-09).
            DataError: If the customer data cannot be loaded.
        """
        # Step 1: Validate (server-side, FR-10)
        validated = validate_query(query)

        # Step 2: Normalize the query
        query_norm = normalize(validated)

        # Step 3: Load customers and filter
        customers = self._repo.load()
        results: list[Customer] = []

        for customer in customers:
            # Normalize each field for comparison (S3, S4)
            name_norm = normalize(customer.name)
            email_norm = normalize(customer.email)

            # Substring match on either field (S1, S2)
            if query_norm in name_norm or query_norm in email_norm:
                results.append(customer)  # Return original values (S6)

        return results  # Empty list if no matches (S7)
