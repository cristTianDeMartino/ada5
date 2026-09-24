# Tasks — Customer Search

> ADA-05 · Ingeniería de Software asistida por IA · UADY
>
> Cada tarea ejecuta lo definido en [`REQUIREMENTS.md`](./REQUIREMENTS.md) y especificado en [`SPEC.md`](./SPEC.md).
> No se introducen requisitos nuevos.

---

## T-01 Project setup

- **Goal:** Crear la estructura de directorios del proyecto, el paquete Python `customer_search`, el archivo de datos de ejemplo y las dependencias de desarrollo.
- **Files:**
  - `customer_search/__init__.py`
  - `customer_search/exceptions.py`
  - `data/customers.json` (dataset inicial con ~20 registros de ejemplo)
  - `tests/__init__.py`
  - `requirements-dev.txt` (`pytest`, `pytest-cov`)
- **Acceptance:**
  - El paquete `customer_search` es importable (`python -c "import customer_search"`).
  - `data/customers.json` es JSON válido y contiene una lista de objetos con campos `id`, `name`, `email`.
  - Las excepciones `ValidationError` y `DataError` son importables desde `customer_search.exceptions`.
- **Verification:**
  ```
  python -c "import customer_search; print('OK')"
  python -c "import json; json.load(open('data/customers.json')); print('JSON OK')"
  python -c "from customer_search.exceptions import ValidationError, DataError; print('Exceptions OK')"
  ```

---

## T-02 Domain model

- **Goal:** Implementar el modelo `Customer` como dataclass y el `CustomerRepository` que carga y cachea los datos desde JSON. Refs: SPEC § Domain Model, ARCHITECTURE § Components.
- **Files:**
  - `customer_search/models.py` — dataclass `Customer(id, name, email)`
  - `customer_search/repository.py` — clase `CustomerRepository` con método `load() → list[Customer]`
- **Acceptance:**
  - `Customer` es una dataclass con campos `id: str`, `name: str`, `email: str` (FR-06).
  - `CustomerRepository` carga `data/customers.json` y devuelve `list[Customer]`.
  - `CustomerRepository` cachea en memoria: la segunda llamada a `load()` no relee el archivo.
  - Si el archivo no existe, lanza `DataError` (SPEC § Error Handling).
- **Verification:**
  ```
  python -c "
  from customer_search.repository import CustomerRepository
  repo = CustomerRepository('data/customers.json')
  customers = repo.load()
  print(f'Loaded {len(customers)} customers')
  print(f'First: {customers[0].name} — {customers[0].email}')
  "
  ```

---

## T-03 Search logic

- **Goal:** Implementar el `Normalizer` (accent/case removal) y el `SearchService` (validar → normalizar → filtrar). Refs: SPEC § Search Rules S1–S7, ARCHITECTURE § Data Flow.
- **Files:**
  - `customer_search/normalizer.py` — funciones `normalize(text) → str`, `remove_accents(text) → str`
  - `customer_search/service.py` — clase `SearchService` con método `search(query) → list[Customer]`
- **Acceptance:**
  - `normalize("José García")` devuelve `"jose garcia"` (FR-03, FR-04).
  - `search("jose")` devuelve registros cuyo nombre o email contengan "jose" sin importar acentos ni mayúsculas (FR-02, FR-03, FR-04, FR-05).
  - `search("@example")` devuelve todos los clientes con ese dominio de email (FR-02, FR-05).
  - `search("zzzznotexist")` devuelve lista vacía `[]` (FR-07).
  - Los resultados contienen los valores **originales** (sin normalizar) de `id`, `name`, `email` (FR-06).
- **Verification:**
  ```
  python -c "
  from customer_search.service import SearchService
  svc = SearchService('data/customers.json')
  results = svc.search('jose')
  for c in results: print(f'{c.name} — {c.email}')
  "
  ```

---

## T-04 Validation and errors

- **Goal:** Implementar el `Validator` y las dos interfaces (CLI y HTTP API) con manejo de errores. Refs: SPEC § Validation Rules V1–V3, SPEC § Error Handling, ARCHITECTURE § Interfaces.
- **Files:**
  - `customer_search/validator.py` — función `validate_query(query) → str` que lanza `ValidationError`
  - `customer_search/api.py` — servidor HTTP en puerto 8000 con endpoint `GET /customers/search?q=`
  - `customer_search/cli.py` — entry point CLI (`python -m customer_search.cli <query>`)
  - `customer_search/__main__.py` — permite `python -m customer_search`
- **Acceptance:**
  - `validate_query("")` lanza `ValidationError` (FR-08).
  - `validate_query("   ")` lanza `ValidationError` (FR-08).
  - `validate_query("Ana  García")` lanza `ValidationError` por doble espacio (FR-09).
  - `validate_query("Ana García")` retorna `"Ana García"` (válido).
  - HTTP `GET /customers/search?q=jose` → `200 {"results": [...], "count": N}` (FR-10, NFR-02).
  - HTTP `GET /customers/search?q=` → `400 {"error": "Query must not be empty"}` (FR-08, FR-10).
  - HTTP `GET /customers/search?q=Ana++García` → `400 {"error": "Query must not contain consecutive spaces"}` (FR-09, FR-10).
  - CLI `python -m customer_search.cli "jose"` → imprime resultados, exit code 0 (NFR-02).
  - CLI `python -m customer_search.cli ""` → imprime error en stderr, exit code 1 (FR-10).
- **Verification:**
  ```
  # Validador
  python -c "
  from customer_search.validator import validate_query
  try: validate_query('')
  except Exception as e: print(f'OK: {e}')
  "

  # CLI
  python -m customer_search.cli "jose"

  # API (en otra terminal)
  python -m customer_search.api &
  curl "http://localhost:8000/customers/search?q=jose"
  curl "http://localhost:8000/customers/search?q="
  ```

---

## T-05 Tests

- **Goal:** Escribir la suite completa de tests automatizados cubriendo todos los test scenarios definidos en SPEC § Test Scenarios (TS-01 → TS-15). Refs: ARCHITECTURE § Testing Strategy.
- **Files:**
  - `tests/test_normalizer.py` — tests unitarios de `Normalizer` (TS-03, TS-04)
  - `tests/test_validator.py` — tests unitarios de `Validator` (TS-07, TS-08, TS-09)
  - `tests/test_service.py` — tests unitarios de `SearchService` (TS-01, TS-02, TS-05, TS-06)
  - `tests/test_api.py` — tests de integración HTTP (TS-11, TS-12)
  - `tests/test_cli.py` — tests de integración CLI (TS-13, TS-14)
  - `tests/test_performance.py` — test de rendimiento con 1 000 registros (TS-10)
- **Acceptance:**
  - Todos los tests pasan: `pytest tests/ -v` → 0 failures.
  - Cobertura ≥ 90 % sobre `customer_search/`: `pytest --cov=customer_search --cov-fail-under=90` (NFR-03).
  - Cada test scenario de SPEC (TS-01 → TS-15) tiene al menos un test correspondiente.
  - El test de performance verifica que la búsqueda sobre 1 000 registros completa en ≤ 200 ms (NFR-01).
- **Verification:**
  ```
  pytest tests/ -v
  pytest tests/ --cov=customer_search --cov-report=term-missing --cov-fail-under=90
  ```

---

## T-06 Documentation

- **Goal:** Actualizar `README.md` con instrucciones de uso, actualizar `AI_USAGE_LOG.md` con todas las interacciones, y verificar que todos los documentos son consistentes entre sí.
- **Files:**
  - `README.md` — descripción del proyecto, instrucciones de instalación, uso (CLI + API), y cómo correr tests.
  - `AI_USAGE_LOG.md` — registro completo de todas las interacciones con IA.
- **Acceptance:**
  - `README.md` incluye: descripción, setup (`pip install -r requirements-dev.txt`), uso de CLI, uso de API, cómo correr tests.
  - `AI_USAGE_LOG.md` tiene una entrada por cada interacción con IA utilizada durante el proyecto.
  - Los IDs referenciados en `SPEC.md` existen en `REQUIREMENTS.md`.
  - Los test scenarios en `SPEC.md` corresponden con los tests implementados en `tests/`.
  - No hay secciones vacías en ningún documento.
- **Verification:**
  ```
  # Verificar que el README tiene las secciones clave
  grep -c "## " README.md

  # Verificar que no hay secciones vacías en los docs
  python -c "
  for f in ['REQUIREMENTS.md','SPEC.md','ARCHITECTURE.md','TASKS.md']:
      print(f'{f}: {len(open(f).readlines())} lines')
  "
  ```
