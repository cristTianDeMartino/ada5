# Requirements — Customer Search

## User Story
As a user,
I want to search customers by name or email,
so that I can quickly find the customer record I need.

## Functional Requirements

| ID    | Requirement |
|-------|-------------|
| FR-01 | The system shall accept a search query string from the user. |
| FR-02 | The system shall search customers by **name** AND **email** simultaneously; the user does NOT select the field — the query is matched against both. |
| FR-03 | The search shall be **case-insensitive** (e.g., `"Ana"` matches `"ana"`, `"ANA"`). |
| FR-04 | The search shall be **accent-insensitive** (e.g., `"jose"` matches `"José"`, `"García"` matches `"garcia"`). |
| FR-05 | The search shall support **partial matching** (substring) on both name and email. |
| FR-06 | The system shall return all matching customer records containing `id`, `name`, and `email`. |
| FR-07 | The system shall return an empty list when no customers match the query. |
| FR-08 | The system shall validate that the search query is a non-empty string of at least 1 character after trimming whitespace. |
| FR-09 | The system shall **reject** queries that contain **consecutive spaces** (two or more spaces in a row); these are considered invalid input. |
| FR-10 | Input validation shall occur **server-side** (in the service layer). Invalid input returns **HTTP 400** with a JSON error body (API) or an **error message** in text (CLI). The client does not pre-filter — the service is the single source of truth for validation. |

## Non-Functional Requirements

| ID     | Requirement |
|--------|-------------|
| NFR-01 | Search response time shall be ≤ 200 ms for a dataset of up to 1 000 customers. |
| NFR-02 | The system shall be usable both as a CLI tool and as an HTTP API (port 8000). |
| NFR-03 | The codebase shall maintain ≥ 90 % test coverage on the search module. |

## Open Questions

| ID   | Question |
|------|----------|
| Q-01 | Should search results be paginated for large result sets? (Deferred — dataset ≤ 1 000.) |
| Q-02 | Should fuzzy/typo-tolerant matching be supported? (Out of scope for v1.) |

## Constraints / Assumptions

| ID   | Description |
|------|-------------|
| C-01 | Customer data is stored in a local JSON file (`data/customers.json`); no external database. |
| A-01 | The initial dataset will contain ≤ 1 000 customer records. |
