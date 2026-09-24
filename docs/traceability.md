# Fase 8 — Matriz de Trazabilidad y Pruebas

> **ADA-05 · Ingeniería de Software asistida por IA · UADY**
> 
> La trazabilidad conecta los requisitos de `REQUIREMENTS.md` con su especificación en `SPEC.md`, la tarea de implementación en `TASKS.md`, los archivos generados y los tests correspondientes, garantizando que todo requisito se puede verificar en el código.

---

## Matriz de Trazabilidad (Fase 8)

| Requirement | SPEC / AC | Task | Files | Test (pytest) | Status | Notes |
|-------------|-----------|------|-------|---------------|--------|-------|
| **FR-01**   | AC-1, AC-6, AC-7 | T-04 | `api.py`, `cli.py` | `TestAPISuccess`, `TestCLIWithResults` | ✅ Done | CLI y HTTP API aceptan el string de consulta (query param `q` o arg CLI). |
| **FR-02**   | S1, AC-1, AC-4 | T-03 | `service.py` | `TestSimultaneousSearch` | ✅ Done | Búsqueda simultánea implementada mediante condicional `OR` en ambos campos. |
| **FR-03**   | S3, AC-2 | T-03 | `normalizer.py` | `TestCaseInsensitive` | ✅ Done | Pipeline de normalización aplica `.lower()` en query y campos. |
| **FR-04**   | S4, AC-3 | T-03 | `normalizer.py` | `TestAccentInsensitive` | ✅ Done | Remoción de acentos mediante normalización Unicode `NFD`. |
| **FR-05**   | S2, AC-1, AC-4 | T-03 | `service.py` | `TestPartialNameSearch`, `TestPartialEmailSearch` | ✅ Done | Implementado mediante operador `in` (substring matching en Python). |
| **FR-06**   | S6 | T-02, T-03 | `models.py`, `service.py` | `TestOriginalValues` | ✅ Done | Retorna dataclass `Customer` original sin mutar los atributos mostrados. |
| **FR-07**   | S7, AC-5 | T-03 | `service.py` | `TestNoResults` | ✅ Done | Lista vacía `[]` si no hay coincidencias; HTTP 200 o CLI exit 0. |
| **FR-08**   | V1, AC-6 | T-04 | `validator.py` | `TestValidateQueryEmpty`, `TestValidateQuerySpacesOnly` | ✅ Done | Validaciones con `strip()` y excepciones en backend. |
| **FR-09**   | V2, AC-7 | T-04 | `validator.py` | `TestValidateQueryConsecutiveSpaces` | ✅ Done | Validación con Regex `r"  +"` antes de iniciar la búsqueda. |
| **FR-10**   | V3, AC-6, AC-7 | T-04 | `service.py`, `api.py`, `cli.py` | `TestAPIValidationErrors`, `TestCLIWithErrors` | ✅ Done | `validator.py` se invoca dentro de `SearchService`; errores `ValidationError` atrapados en endpoints y CLI para retornar 400 o error a `stderr`. |
| **NFR-01**  | AC-8 | T-05 | N/A | `TestPerformance` | ✅ Done | Test verifica ≤ 200ms para 1 000 registros (se ejecuta en aprox ~1-3ms). |
| **NFR-02**  | AC-9 | T-04 | `cli.py`, `api.py`, `__main__.py` | `TestAPIMain`, `TestCLIMainDirect` | ✅ Done | Servidor web con `http.server` y script de CLI `sys.argv`. |
| **NFR-03**  | AC-10 | T-05 | `tests/*` | Módulo `pytest-cov` | ✅ Done | Cobertura final lograda de **95%** (requerida ≥ 90%). |

---

## Fase 9 — Ejecución de Pruebas Automatizadas

Cada criterio de aceptación definido en `SPEC.md` está automatizado bajo el framework **pytest**.

**Resumen de ejecución:**
```text
============================= test session starts =============================
platform win32 -- Python 3.14.6, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\cdmr9\Documents\UADY\UADY\7 SEMESTRE\OPTA IA\ADA5
plugins: cov-7.1.0
collected 61 items

tests/test_api.py::TestAPISuccess::test_search_returns_200_with_results PASSED [  1%]
tests/test_api.py::TestAPISuccess::test_search_jose_accent_insensitive PASSED [  3%]
tests/test_api.py::TestAPISuccess::test_no_results_returns_200_empty PASSED [  4%]
tests/test_api.py::TestAPIValidationErrors::test_empty_query_returns_400 PASSED [  6%]
...
tests/test_normalizer.py::TestRemoveAccents::test_removes_acute_accents PASSED [ 34%]
tests/test_normalizer.py::TestNormalize::test_full_pipeline PASSED       [ 50%]
tests/test_performance.py::TestPerformance::test_search_1000_records_under_200ms PASSED [ 55%]
tests/test_service.py::TestSimultaneousSearch::test_garcia_matches_name_and_email PASSED [ 73%]
tests/test_validator.py::TestValidateQueryConsecutiveSpaces::test_double_space_raises PASSED [ 95%]
...
============================= 61 passed in 3.11s ==============================
```

- Se ejecutaron un total de **61 pruebas unitarias y de integración**.
- **0 fallos**.
- **Cobertura validada**: 94.67%.

### Mapeo de Tests a Criterios de Aceptación (AC)

Todos los tests son rastreables hasta `SPEC.md` y, por consiguiente, a los Requisitos:

- **AC-1 (Partial Match):** `test_partial_name_mar`, `test_partial_email_domain` rastreables a FR-02/FR-05.
- **AC-2 (Case Insensitive):** `test_lowercase`, `test_uppercase_query` rastreables a FR-03.
- **AC-3 (Accent Insensitive):** `test_accent_removal`, `test_no_accent_matches_accented` rastreables a FR-04.
- **AC-4 (Simultaneous):** `test_garcia_matches_name_and_email` rastreable a FR-02.
- **AC-5 (No match -> Empty):** `test_no_match_returns_empty`, `test_no_results_exit_0` rastreables a FR-07.
- **AC-6 (Empty Validation):** `test_empty_query_returns_400`, `test_empty_query_shows_error_on_stderr` rastreables a FR-08.
- **AC-7 (Double Space Validation):** `test_double_space_raises`, `test_double_space_validation_error` rastreables a FR-09.
- **AC-8 (Performance):** `test_search_1000_records_under_200ms` rastreable a NFR-01.
- **AC-9 (API & CLI exposure):** Todo `test_api.py` y `test_cli.py` rastreable a NFR-02.
- **AC-10 (Coverage >= 90%):** Validado por la ejecución con `--cov-fail-under=90` rastreable a NFR-03.
