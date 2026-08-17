# Kardex RAG — Copiloto Analítico para Inventarios

**Estado: proyecto cerrado.** Sprint de 7 días completo + mejoras de UI post-sprint.
Único pendiente: grabar el video demo (ver [`DEMO.md`](./DEMO.md)).

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
DEMO.md          guion para grabar el video demo
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

### Opción rápida: todo en Docker

```bash
docker compose up -d --build
docker exec -it kardex_rag_ollama ollama pull phi3
docker exec -it kardex_rag_ollama ollama pull nomic-embed-text
cd backend && python -m app.rag.ingest   # una sola vez, para cargar el CSV
```

Levanta los 4 servicios (DB, Ollama, backend, frontend) contenedorizados, con
hot-reload (`backend/` y `frontend/` están montados como volumen). Backend en
`http://localhost:8000`, frontend en `http://localhost:5173`. La ingesta
(`python -m app.rag.ingest`) todavía requiere el venv local (ver sección 2)
porque no hay un comando de un solo paso dentro del contenedor.

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
python -m app.main
```

Probar: `curl http://localhost:8000/api/health` → `{"status":"ok","database":"connected"}`

> **Nota (Windows):** se corre con `python -m app.main` y no con el CLI
> `uvicorn app.main:app --reload` directo. `psycopg` en modo async (usado por
> el vectorstore de `/api/chat`) no soporta el `ProactorEventLoop`, que es el
> default de asyncio en Windows; `app/main.py` fuerza `SelectorEventLoop`
> antes de que uvicorn cree su loop. Ademas hace falta pasar `loop="none"` a
> `uvicorn.run()`: por default, uvicorn hardcodea `ProactorEventLoop` en
> Windows sin importar que policy este activa. No afecta Docker/Linux.
>
> Si despues de reiniciar el backend las respuestas no cambian (parece que
> el codigo nuevo no se aplico), puede haber un proceso `python.exe` viejo
> huerfano todavia escuchando el puerto: `tasklist //FI "IMAGENAME eq
> python.exe"` para verlos todos y matarlos por PID antes de levantar uno
> limpio (matar solo el proceso "reloader" de uvicorn no siempre mata al
> worker hijo).

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
> Las respuestas pueden tardar. El control de preguntas fuera de contexto no
> depende solo del prompt (un modelo chico como `phi3` no lo seguía de forma
> confiable) sino de un guardrail por score de similitud — ver `CLAUDE.md`
> sección 8, Día 6.

### 5. Probar el endpoint `/api/chat` (streaming)

Con el backend corriendo (`python -m app.main`):

```bash
curl -N -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "Que productos estan agotados?"}'
```

`-N` desactiva el buffering de curl para ver los eventos SSE (`data: {"content": "..."}`)
llegar token por token en vez de todos juntos al final.

### 6. Frontend

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
| 4   | Exposición y Conexión (`/api/chat` con streaming)          | ✅ Completo |
| 5   | Interfaz de Usuario (chat en Vue)                          | ✅ Completo |
| 6   | Depuración y Análisis (anti-alucinación, UI generativa)    | ✅ Completo |
| 7   | Retrospectiva y Documentación                              | ✅ Completo |
| —   | Post-sprint: UI con glassmorphism + GSAP, paleta monocromática | ✅ Completo |

Detalle completo de cada fase en [`CLAUDE.md`](./CLAUDE.md), sección 7 (roadmap)
y sección 8 (estado actual, con el detalle de cada hito y los bugs reales
encontrados en el camino). Guion para grabar la demo: [`DEMO.md`](./DEMO.md).

## Seguridad

- Ninguna API key vive en el código fuente; todo se configura vía `.env` (nunca
  commiteado — ver `.gitignore`).
- Inputs hacia el LLM y hacia SQL se sanitizan; las queries usan el driver
  parametrizado (nunca concatenación de SQL).
