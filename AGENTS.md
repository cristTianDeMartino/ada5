# Agent Instructions

> ADA-05 · Ingeniería de Software asistida por IA · UADY
>
> Directrices que el agente de IA debe seguir durante todo el desarrollo del proyecto.

---

## Project Rules

- Read [`REQUIREMENTS.md`](./REQUIREMENTS.md) before implementing.
- Read [`SPEC.md`](./SPEC.md) before implementing.
- Read [`ARCHITECTURE.md`](./ARCHITECTURE.md) before architectural changes.
- Follow [`TASKS.md`](./TASKS.md).
- Prefer small, focused changes.
- Do not invent business requirements.
- Do not modify `REQUIREMENTS.md` or `SPEC.md` to make tests pass.
- Do not delete or weaken tests.
- Do not add dependencies without justification.

---

## Validation

- Run `pytest` before and after changes.
- Add tests for new behavior.
- Report changed files and test results.
- Stop and ask for clarification if requirements conflict.

---

## Definition of Done

- Relevant tests pass.
- Acceptance criteria are covered.
- No unrelated files are changed.
- Documentation reflects final behavior.
