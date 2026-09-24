"""Customer domain model.

Defines the Customer dataclass per SPEC.md § Domain Model.
Fields: id, name, email (all str) — FR-06.
"""

from dataclasses import dataclass


@dataclass
class Customer:
    """A customer record with id, name, and email."""

    id: str
    name: str
    email: str
