# Kardex RAG — Copiloto Analítico para Inventarios

Copiloto con IA (RAG) para un sistema de facturación y bodegas: permite consultar en
lenguaje natural el estado del Kardex, traslados de bodega y reportes, en vez de
navegar tablas y filtros.

> Contexto completo del proyecto (rol del asistente, convenciones, roadmap del sprint):
> ver [`CLAUDE.md`](./CLAUDE.md).

## Stack

| Capa                        | Tecnología                                             |
| ---------------------------- | ------------------------------------------------------- |
| Frontend                     | Vue.js 3 (Composition API) + Vite + TypeScript          |
| Backend                      | Python + FastAPI (async)                                |
| Orquestación IA              | LangChain                                                |
| Base de datos / memoria vectorial | PostgreSQL + `pgvector`                             |
| LLM                          | Ollama (`phi3`, local) por defecto — alternativa: OpenAI API |
| Infraestructura              | Docker / Docker Compose                                  |

## Estructura del repo

```
/backend        FastAPI async — api/core/rag/models, tests, Dockerfile
/frontend        Vue 3 + Vite + TS — components/views/composables, Dockerfile
/infra           init.sql (habilita pgvector)
docker-compose.yml
.env.example
```

## Requisitos

- Docker Desktop
- Python 3.12+
- Node.js 22+

## Setup rápido

```bash
cp .env.example .env
```

Por defecto usa Ollama local (no requiere API key). Para usar OpenAI, editá `.env`
y comentá/descomentá las secciones correspondientes.

### 1. Infraestructura (DB + LLM)

```bash
docker compose up -d db ollama
docker exec -it kardex_rag_ollama ollama pull phi3
```

> **Nota:** el servicio `db` mapea el puerto host **5433** (no 5432) para evitar
> conflictos con un PostgreSQL nativo que pueda estar corriendo en la máquina.
> Ajustá `DATABASE_URL` en tu `.env` si tu setup no tiene ese conflicto.

Verificar que `pgvector` esté habilitado:

```bash
docker exec -it kardex_rag_db psql -U kardex_admin -d kardex_rag -c "\dx"
```

### 2. Backend

```bash
cd backend
python -m venv .venv
source .venv/Scripts/activate   # Windows (Git Bash) — usar .venv/bin/activate en Linux/Mac
pip install -r requirements-dev.txt
uvicorn app.main:app --reload
```

Probar: `curl http://localhost:8000/api/health` → `{"status":"ok","database":"connected"}`

### 3. Ingesta de datos (Kardex → pgvector)

Requiere el modelo de embeddings local en Ollama (una sola vez, ~274MB):

```bash
docker exec -it kardex_rag_ollama ollama pull nomic-embed-text
```

Con el backend y la DB corriendo:

```bash
cd backend
python -m app.rag.ingest
```

Carga `backend/data/kardex.csv` (50 registros ficticios) a la colección `kardex`
en pgvector, vía `langchain-postgres`.

### 4. Probar la cadena RAG por consola

Requiere el modelo de chat en Ollama (una sola vez, ~2.2GB):

```bash
docker exec -it kardex_rag_ollama ollama pull phi3
```

```bash
cd backend
python -m app.rag.console
```

> **Nota:** `phi3` corre en CPU en la mayoría de los setups locales (~10 tok/s).
> Las respuestas pueden tardar. Es un modelo chico: puede no negarse siempre a
> responder preguntas fuera del contexto del Kardex — ver `CLAUDE.md` sección 8.

### 5. Frontend

```bash
cd frontend
npm install
npm run dev
```

Abrir `http://localhost:5173`.

## Calidad de código

**Backend** (`ruff` para lint + format, `pytest` para tests):

```bash
cd backend
ruff check .
ruff format --check .
pytest
```

**Frontend** (`eslint` + `prettier`, type-check vía `vue-tsc`):

```bash
cd frontend
npm run lint
npm run format:check
npm run build   # incluye type-check (vue-tsc -b)
```

### Pre-commit hooks

El repo usa [pre-commit](https://pre-commit.com/) para correr lint/format
automáticamente antes de cada commit (backend con `ruff`, frontend con
`eslint`/`prettier`).

```bash
pip install pre-commit
pre-commit install
```

### CI

GitHub Actions corre lint, format-check, build y tests en cada push/PR a `main`
que toque `backend/` o `frontend/` (ver `.github/workflows/`).

## Roadmap del sprint (7 días)

| Día | Hito                                                    | Estado |
| --- | -------------------------------------------------------- | ------ |
| 1   | Infraestructura y Setup                                   | ✅ Completo |
| 2   | Datos y Memoria (ingesta CSV → embeddings → pgvector)      | ✅ Completo |
| 3   | Cerebro de la IA (cadena RAG, retriever, system prompt)    | ✅ Completo |
| 4   | Exposición y Conexión (`/api/chat` con streaming)          | Pendiente |
| 5   | Interfaz de Usuario (chat en Vue)                          | Pendiente |
| 6   | Depuración y Análisis (anti-alucinación, UI generativa)    | Pendiente |
| 7   | Retrospectiva y Documentación                              | Pendiente |

Detalle completo de cada fase en [`CLAUDE.md`](./CLAUDE.md), sección 7.

## Seguridad

- Ninguna API key vive en el código fuente; todo se configura vía `.env` (nunca
  commiteado — ver `.gitignore`).
- Inputs hacia el LLM y hacia SQL se sanitizan; las queries usan el driver
  parametrizado (nunca concatenación de SQL).
