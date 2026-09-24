# SPEC — Customer Search Feature

> ADA-05 · Ingeniería de Software asistida por IA · UADY

## Goal

Proveer una función de búsqueda de clientes que, dado un texto libre, devuelva todos los registros cuyo **nombre** o **correo electrónico** coincidan parcialmente con la consulta, sin que el usuario tenga que indicar en qué campo buscar. La función se expone como **CLI** y como **HTTP API** sobre el mismo motor de búsqueda.

---

## Requirements Covered

| Tipo       | IDs |
|------------|-----|
| Funcional  | FR-01, FR-02, FR-03, FR-04, FR-05, FR-06, FR-07, FR-08, FR-09, FR-10 |
| No funcional | NFR-01, NFR-02, NFR-03 |

> Todos los IDs están definidos en [`REQUIREMENTS.md`](./REQUIREMENTS.md). Este documento **no** duplica su contenido; solo los referencia.

---

## Scope

- Motor de búsqueda con partial match, case-insensitive y accent-insensitive sobre `name` y `email` simultáneamente (FR-02, FR-03, FR-04, FR-05).
- Validación server-side del query (FR-08, FR-09, FR-10).
- Interfaz CLI (`python -m src.cli <query>`) y HTTP API (`GET /customers/search?q=<query>` en puerto 8000) (NFR-02).
- Dataset almacenado en `data/customers.json` (C-01), hasta 1 000 registros (A-01).
- Suite de tests automatizados con cobertura ≥ 90 % (NFR-03).

---

## Out of Scope

| Excluido | Justificación |
|----------|---------------|
| Paginación de resultados | Q-01: diferido; dataset ≤ 1 000 registros no lo requiere. |
| Búsqueda fuzzy / tolerante a typos | Q-02: fuera de alcance para v1. |
| CRUD de clientes (crear, editar, eliminar) | Esta spec cubre únicamente la búsqueda; los datos se precargan desde JSON. |
| Autenticación / autorización | No aplica para herramienta local de desarrollo. |
| Base de datos externa | C-01: se usa JSON local. |

---

## Domain Model

```
┌─────────────────────────────┐
│          Customer           │
├─────────────────────────────┤
│  id    : str  (UUID)        │
│  name  : str                │
│  email : str                │
└─────────────────────────────┘
```

- **id** — Identificador único del cliente (UUID v4, generado al poblar el dataset).
- **name** — Nombre completo. Puede contener acentos, mayúsculas, espacios simples.
- **email** — Correo electrónico. Siempre en minúsculas por convención.

Estructura JSON de ejemplo (`data/customers.json`):
```json
[
  { "id": "a1b2c3d4", "name": "María García", "email": "maria.garcia@example.com" },
  { "id": "e5f6g7h8", "name": "José López",  "email": "jose.lopez@example.com"  }
]
```

---

## Search Rules

| #  | Regla | Refs |
|----|-------|------|
| S1 | El query se compara simultáneamente contra `name` **y** `email`; un match en cualquiera de los dos incluye al cliente en los resultados. | FR-02 |
| S2 | La comparación es **substring** (parcial): `"gar"` matchea `"María García"` y `"garcia@mail.com"`. | FR-05 |
| S3 | La comparación es **case-insensitive**: antes de comparar, tanto el query como los campos se convierten a minúsculas. | FR-03 |
| S4 | La comparación es **accent-insensitive**: antes de comparar, se aplica normalización Unicode NFD y se eliminan los combining diacritical marks (`\u0300-\u036f`). Así `"jose"` matchea `"José"` y `"García"` matchea `"garcia"`. | FR-04 |
| S5 | El orden de normalización es: (1) strip/trim, (2) normalizar acentos, (3) lowercase, (4) substring match. | FR-03, FR-04, FR-05 |
| S6 | Los resultados se devuelven como lista de objetos `{id, name, email}` con los valores **originales** (sin normalizar). | FR-06 |
| S7 | Si ningún registro matchea, se devuelve una lista vacía `[]`. | FR-07 |

---

## Validation Rules

| #  | Regla | Refs | Ejemplo inválido |
|----|-------|------|-----------------|
| V1 | El query no puede estar vacío ni ser solo espacios en blanco (después de trim). | FR-08 | `""`, `"   "` |
| V2 | El query no puede contener **dos o más espacios consecutivos**. | FR-09 | `"Ana  García"`, `"test   email"` |
| V3 | La validación se ejecuta **en la capa de servicio** (server-side), nunca en el cliente. | FR-10 | — |

> **Motivo de V3** (decisión documentada en `AI_USAGE_LOG.md`, entrada 2):
> - Fuente única de verdad (CLI y API comparten la misma validación).
> - Seguridad: llamadas directas a la API no la pueden saltar.
> - Semántica HTTP correcta: 400 Bad Request.
> - Testeabilidad: un solo punto de test.

---

## Error Handling

| Situación | Interfaz HTTP | Interfaz CLI | Refs |
|-----------|---------------|-------------|------|
| Query vacío o solo espacios | `400 Bad Request` — `{"error": "Query must not be empty"}` | `Error: Query must not be empty` (stderr, exit code 1) | FR-08, FR-10 |
| Query con doble espacio | `400 Bad Request` — `{"error": "Query must not contain consecutive spaces"}` | `Error: Query must not contain consecutive spaces` (stderr, exit code 1) | FR-09, FR-10 |
| Sin resultados (query válido) | `200 OK` — `{"results": [], "count": 0}` | `No customers found.` (stdout, exit code 0) | FR-07 |
| Archivo de datos no encontrado | `500 Internal Server Error` — `{"error": "Customer data file not found"}` | `Error: Customer data file not found` (stderr, exit code 1) | — |

---

## Acceptance Criteria

| AC   | Criterio | Refs |
|------|----------|------|
| AC-1 | Buscar `"mar"` devuelve clientes cuyo nombre **o** email contengan `"mar"` (e.g., "María", "marcos@..."). | FR-02, FR-05 |
| AC-2 | Buscar `"GARCIA"` devuelve `"María García"` (case-insensitive). | FR-03 |
| AC-3 | Buscar `"jose"` devuelve `"José López"` (accent-insensitive). | FR-04 |
| AC-4 | Buscar `"garcia"` devuelve tanto a `"María García"` (por nombre) como a `"garcia@mail.com"` (por email). | FR-02, FR-05 |
| AC-5 | Buscar `"zzzznotexist"` devuelve lista vacía `[]` y HTTP 200. | FR-07 |
| AC-6 | Enviar query `""` (vacío) devuelve HTTP 400 con mensaje de error. | FR-08, FR-10 |
| AC-7 | Enviar query `"Ana  García"` (doble espacio) devuelve HTTP 400 con mensaje de error. | FR-09, FR-10 |
| AC-8 | La búsqueda sobre 1 000 registros responde en ≤ 200 ms. | NFR-01 |
| AC-9 | La misma función de búsqueda es accesible vía CLI y vía HTTP API en puerto 8000. | NFR-02 |
| AC-10 | La cobertura de tests del módulo de búsqueda es ≥ 90 %. | NFR-03 |

---

## Test Scenarios

| ID   | Escenario | Tipo | ACs |
|------|-----------|------|-----|
| TS-01 | Búsqueda parcial por nombre — query `"mar"` devuelve registros con "María", "Marcos", etc. | Unit | AC-1 |
| TS-02 | Búsqueda parcial por email — query `"@example"` devuelve todos los `@example.com`. | Unit | AC-1 |
| TS-03 | Case-insensitive — query `"GARCIA"` matchea `"García"`. | Unit | AC-2 |
| TS-04 | Accent-insensitive — query `"jose"` matchea `"José"`. | Unit | AC-3 |
| TS-05 | Simultaneidad nombre + email — query que aparece en ambos campos devuelve la unión. | Unit | AC-4 |
| TS-06 | Sin resultados — query sin match devuelve `[]`. | Unit | AC-5 |
| TS-07 | Validación: query vacío → error. | Unit | AC-6 |
| TS-08 | Validación: query solo espacios → error. | Unit | AC-6 |
| TS-09 | Validación: doble espacio → error. | Unit | AC-7 |
| TS-10 | Performance: 1 000 registros, búsqueda ≤ 200 ms. | Performance | AC-8 |
| TS-11 | HTTP API: `GET /customers/search?q=mar` → 200 con resultados JSON. | Integration | AC-9 |
| TS-12 | HTTP API: `GET /customers/search?q=` → 400 con error JSON. | Integration | AC-6, AC-9 |
| TS-13 | CLI: `python -m src.cli "mar"` → salida con resultados. | Integration | AC-9 |
| TS-14 | CLI: `python -m src.cli ""` → error en stderr, exit code 1. | Integration | AC-6, AC-9 |
| TS-15 | Cobertura ≥ 90 % reportada por `pytest --cov`. | Coverage | AC-10 |

---

## Constraints

| ID   | Constraint | Origen |
|------|-----------|--------|
| C-01 | Datos en archivo JSON local (`data/customers.json`), sin base de datos externa. | REQUIREMENTS.md C-01 |
| A-01 | Dataset ≤ 1 000 registros. | REQUIREMENTS.md A-01 |
| C-02 | Python 3.10+ como runtime. Dependencias mínimas: solo stdlib + `pytest` para tests + `http.server` o framework ligero para la API. | Decisión de arquitectura |

---

## Open Questions

| ID   | Pregunta | Estado |
|------|----------|--------|
| Q-01 | ¿Se debe paginar para datasets grandes? | Diferido — A-01 limita a ≤ 1 000. |
| Q-02 | ¿Soporte de búsqueda fuzzy? | Fuera de alcance v1. |
