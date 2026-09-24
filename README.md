# ADA 05: Customer Search

> **spec-Driven Feature**
> 
> Construir una feature pequeña siguiendo requirements → specification → architecture → tasks → implementation → tests. El foco es demostrar que una especificación estructurada puede convertirse en trabajo ejecutable por un coding agent.

Este repositorio contiene un motor de búsqueda de clientes (por nombre o email) con soporte para búsqueda parcial, y omisión de acentos/mayúsculas (case-insensitive, accent-insensitive). Se puede usar mediante línea de comandos (CLI) o mediante una API HTTP local.

---

## 🚀 Instalación y Setup

El proyecto requiere Python 3.10+ y no tiene dependencias de producción.

1. Clonar o abrir el repositorio.
2. (Opcional) Crear un entorno virtual.
3. Instalar las dependencias de desarrollo:
   ```bash
   pip install -r requirements-dev.txt
   ```

---

## 💻 Uso como CLI

Busca clientes directamente desde la terminal. Los errores se imprimen en `stderr` (exit code 1).

```bash
python -m src.cli <query>
```

**Ejemplos:**
```bash
# Búsqueda por nombre (ignora acentos y mayúsculas)
python -m src.cli "jose"

# Búsqueda por email
python -m src.cli "@example.com"

# Error de validación (espacios consecutivos)
python -m src.cli "Ana  García"
```

---

## 🌐 Uso como HTTP API

Levanta un servidor HTTP ligero en el puerto 8000 por defecto.

```bash
python -m src
```

**Endpoints:**
- `GET /customers/search?q=<query>`

**Ejemplo con curl:**
```bash
curl "http://localhost:8000/customers/search?q=garcia"
```
**Respuesta:**
```json
{
  "results": [
    {
      "id": "c001",
      "name": "María García",
      "email": "maria.garcia@example.com"
    }
  ],
  "count": 1
}
```

---

## 🧪 Tests y Cobertura

El proyecto usa `pytest` y `pytest-cov` para pruebas unitarias, de integración y de performance. La cobertura requerida es ≥ 90%.

Para ejecutar los tests y ver el reporte de cobertura:
```bash
pytest tests/ --cov=src --cov-report=term-missing --cov-fail-under=90
```

---

## 📂 Documentación del Proyecto

El ciclo de desarrollo guiado por especificaciones se documenta en los siguientes archivos:

1. **[`REQUIREMENTS.md`](./REQUIREMENTS.md)**: Requisitos funcionales (FR) y no funcionales (NFR).
2. **[`SPEC.md`](./SPEC.md)**: Especificación detallada (Reglas, Criterios de Aceptación, Escenarios de Prueba).
3. **[`ARCHITECTURE.md`](./ARCHITECTURE.md)**: Diseño de componentes, flujos de datos y decisiones técnicas.
4. **[`TASKS.md`](./TASKS.md)**: Tareas incrementales implementadas para este proyecto.
5. **[`AGENT.md`](./AGENT.md)**: Reglas seguidas por el agente de IA.
6. **[`AI_USAGE_LOG.md`](./AI_USAGE_LOG.md)**: Registro de interacciones, prompts y decisiones arquitectónicas tomadas junto a la IA.