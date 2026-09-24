# AI Usage Log — ADA 05: Customer Search

> Registro de todas las interacciones con IA durante el desarrollo de esta actividad.

## Metadata

| Campo         | Valor                        |
|---------------|------------------------------|
| Proyecto      | ADA 05 — Spec-Driven Feature |
| Feature       | Customer Search              |
| Herramienta   | Google Antigravity (Claude)   |
| Inicio        | 2026-09-23                   |

---

## Registro de Interacciones

### 1 — Creación de REQUIREMENTS.md
| Campo       | Detalle |
|-------------|---------|
| Fecha/Hora  | 2026-09-23 19:39 CST |
| Prompt      | Implementar función de Customer Search con búsqueda por nombre/email, búsqueda parcial, validación y pruebas. Definir FR/NFR en REQUIREMENTS.md. |
| Artefacto   | `REQUIREMENTS.md` |
| Qué generó  | Documento completo de requisitos: 6 FR (FR-01→FR-06), 3 NFR (NFR-01→NFR-03), 2 Open Questions, 1 Constraint, 1 Assumption. |
| Revisión    | modificado |
| Decisiones  | Se eligió búsqueda case-insensitive parcial; datos en JSON local; doble interfaz CLI + HTTP. |

---

### 2 — Refinamiento de REQUIREMENTS.md (FRs expandidos)
| Campo       | Detalle |
|-------------|---------|
| Fecha/Hora  | 2026-09-23 20:09 CST |
| Prompt      | Especificar mayúsculas/acentos en búsqueda, rechazar doble espacio, búsqueda simultánea nombre+email (usuario no elige campo), y decisión: ¿validar antes de enviar o validar server-side con 400? |
| Artefacto   | `REQUIREMENTS.md` |
| Qué generó  | Expansión de 6 FR → 10 FR. Nuevos: FR-02 (búsqueda simultánea), FR-03 (case-insensitive), FR-04 (accent-insensitive), FR-05 (partial match), FR-08 (trim + no vacío), FR-09 (rechazo doble espacio), FR-10 (validación server-side → 400/error). |
| Revisión    | aceptado |
| Decisiones  | **Decisión: validar server-side (HTTP 400 / mensaje de error).** Motivos: (1) fuente única de verdad — la validación vive en la capa de servicio, CLI y API la comparten sin duplicar código; (2) seguridad — si solo se valida en cliente, llamadas directas a la API la saltan; (3) semántica HTTP — 400 Bad Request es el código estándar para input inválido; (4) testeabilidad — más fácil testear la validación en un solo punto (servicio) que en múltiples clientes. |

---

### 3 — Creación de SPEC.md
| Campo       | Detalle |
|-------------|---------|
| Fecha/Hora  | 2026-09-23 20:18 CST |
| Prompt      | Crear SPEC.md con secciones: Goal, Requirements Covered, Scope, Out of Scope, Domain Model, Search Rules, Validation Rules, Error Handling, Acceptance Criteria, Test Scenarios, Constraints, Open Questions. Sin secciones vacías. IDs deben existir en REQUIREMENTS.md. |
| Artefacto   | `SPEC.md` |
| Qué generó  | Spec completa: Goal, 13 FRs+NFRs cubiertos, scope con 5 puntos, 5 exclusiones, modelo Customer (id/name/email), 7 reglas de búsqueda (S1–S7), 3 reglas de validación (V1–V3), tabla de error handling (4 escenarios × 2 interfaces), 10 acceptance criteria (AC-1→AC-10), 15 test scenarios (TS-01→TS-15), 3 constraints, 2 open questions. |
| Revisión    | <!-- ¿Aceptado tal cual / modificado / rechazado? --> |
| Decisiones  | Se incluyeron FR-07→FR-10 (los nuevos) en Requirements Covered además de los 6 originales. Se definió pipeline de normalización: trim → NFD accent strip → lowercase → substring match. Se mapeó cada AC y TS a sus FRs/NFRs correspondientes para trazabilidad. |

---

### 4 — Creación de ARCHITECTURE.md
| Campo       | Detalle |
|-------------|---------|
| Fecha/Hora  | 2026-09-23 20:25 CST |
| Prompt      | Crear Architecture con secciones: Overview, Components, Responsibilities, Data Flow, Interfaces, Error Handling, Testing Strategy, Dependencies, Design Decisions, Trade-offs. Incluir diagramas Mermaid. |
| Artefacto   | `ARCHITECTURE.md` |
| Qué generó  | Arquitectura 3 capas (interfaces → servicio → datos). 7 componentes definidos con archivos. 4 diagramas Mermaid: flowchart de componentes, class diagram de responsabilidades, 2 sequence diagrams (flujo exitoso y validación fallida). API spec (GET /customers/search), CLI spec con ejemplos. 6 decisiones de diseño (DD-1→DD-6), 5 trade-offs documentados. Cero dependencias externas en producción. |
| Revisión    | <!-- ¿Aceptado tal cual / modificado / rechazado? --> |
| Decisiones  | stdlib http.server en vez de Flask/FastAPI (DD-2); unicodedata.normalize NFD para acentos (DD-3); excepciones custom ValidationError/DataError (DD-5); Normalizer como funciones puras sin clase (DD-6); búsqueda lineal O(n) aceptable para ≤ 1 000 registros. |

---

### 5 — Creación de TASKS.md
| Campo       | Detalle |
|-------------|---------|
| Fecha/Hora  | 2026-09-23 20:35 CST |
| Prompt      | Crear TASKS.md con 6 tareas (T-01→T-06): Project setup, Domain model, Search logic, Validation and errors, Tests, Documentation. Cada tarea con Goal, Files, Acceptance, Verification. No introducir requisitos nuevos. |
| Artefacto   | `TASKS.md` |
| Qué generó  | 6 tareas con: goals concretos referenciando secciones de SPEC/ARCHITECTURE, archivos a crear por tarea, criterios de aceptación mapeados a FRs/NFRs, comandos de verificación ejecutables. T-01 (setup: paquete + JSON + exceptions), T-02 (model + repository), T-03 (normalizer + service), T-04 (validator + API + CLI), T-05 (15 test scenarios), T-06 (README + AI_USAGE_LOG). |
| Revisión    | <!-- ¿Aceptado tal cual / modificado / rechazado? --> |
| Decisiones  | Se ordenaron las tareas por dependencia (setup → model → search → validation → tests → docs). Cada tarea es independientemente verificable con comandos de terminal. |

---

### 6 — Creación de AGENT.md
| Campo       | Detalle |
|-------------|---------|
| Fecha/Hora  | 2026-09-23 20:37 CST |
| Prompt      | Crear Agent Instructions con secciones: Project Rules, Validation, Definition of Done. Reglas sobre leer docs antes de implementar, no inventar requisitos, no debilitar tests, correr pytest antes/después de cambios. |
| Artefacto   | `AGENT.md` |
| Qué generó  | Documento con 9 project rules (leer docs, cambios pequeños, no inventar requisitos, no modificar REQUIREMENTS/SPEC para pasar tests, no borrar tests, no agregar deps sin justificación), 4 reglas de validación (pytest, tests para nuevo behavior, reportar archivos y resultados, pedir clarificación si hay conflictos), 4 criterios de Definition of Done. |
| Revisión    | <!-- ¿Aceptado tal cual / modificado / rechazado? --> |
| Decisiones  | Se enlazaron los documentos referenciados con links relativos para navegabilidad. |

---

### 7 — Implementación T-01: Project setup
| Campo       | Detalle |
|-------------|---------|
| Fecha/Hora  | 2026-09-23 20:48 CST |
| Prompt      | Seguir protocolo AGENT.md: leer todos los docs, inspeccionar repo, identificar siguiente tarea incompleta (T-01), implementarla y verificarla. |
| Artefacto   | `src/__init__.py`, `src/exceptions.py`, `data/customers.json`, `tests/__init__.py`, `requirements-dev.txt` |
| Qué generó  | Estructura del proyecto: paquete Python importable, 2 excepciones custom (ValidationError, DataError), dataset JSON con 20 clientes (nombres con acentos/ñ, 2 dominios de email), paquete de tests, dependencias dev (pytest, pytest-cov). |
| Revisión    | <!-- ¿Aceptado tal cual / modificado / rechazado? --> |
| Decisiones  | Se detectó problema de encoding cp1252 en Windows al leer JSON con acentos; se anotó que el Repository (T-02) debe usar `encoding='utf-8'` explícitamente. Dataset incluye variedad de acentos (á, é, í, ó, ú, ñ) para facilitar tests de accent-insensitive. |

---

### 8 — Implementación T-02 a T-05: Model, Logic, Validation & Tests
| Campo       | Detalle |
|-------------|---------|
| Fecha/Hora  | 2026-09-23 21:13 CST |
| Prompt      | Haz todas las tareas (T-02 a T-05) |
| Artefacto   | `src/` (models.py, repository.py, normalizer.py, service.py, validator.py, api.py, cli.py, \_\_main\_\_.py), `tests/` |
| Qué generó  | Se implementó el Domain Model (Data class y repo cacheado). Search Logic con pipeline de normalización sin acentos/case. Validation server-side para queries vacíos o espacios consecutivos. HTTP API con `http.server` estándar y un CLI funcional. Suite de pruebas completa (61 pruebas unitarias e integración). |
| Revisión    | Aceptado |
| Decisiones  | 1. Forzar encoding `utf-8` en repositorio (fix `cp1252` en Windows). 2. Agregar test de error en `api.py` (monkeypatch) para alcanzar cobertura >90%. 3. Agregar test directo `cli.main()` para cubrir código no reportado al correr vía `subprocess`. (Se logró cobertura del 95%). |

---

### 9 — Documentación final (T-06)
| Campo       | Detalle |
|-------------|---------|
| Fecha/Hora  | 2026-09-23 21:31 CST |
| Prompt      | Seguir con la tarea (T-06: Documentación). |
| Artefacto   | `README.md`, `AI_USAGE_LOG.md` |
| Qué generó  | Actualización completa del README con guía de instalación, ejemplos CLI, ejemplos API y cómo correr pruebas. Registro final en AI_USAGE_LOG. |
| Revisión    | Aceptado |
| Decisiones  | Referenciar todos los `.md` en el README para que la especificación esté visible a simple vista y demuestre el flujo `requirements → spec → implementation`. |

---

---

<!-- 
## Plantilla para nuevas entradas (copiar y pegar)

### N — Título breve
| Campo       | Detalle |
|-------------|---------|
| Fecha/Hora  |  |
| Prompt      |  |
| Artefacto   |  |
| Qué generó  |  |
| Revisión    |  |
| Decisiones  |  |

---
-->
