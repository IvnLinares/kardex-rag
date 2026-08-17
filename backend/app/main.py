import asyncio
import sys

# psycopg (usado por langchain-postgres en modo async) no soporta el
# ProactorEventLoop, que es el default de asyncio en Windows. Hay que fijar
# el SelectorEventLoop ANTES de que uvicorn cree el loop (por eso el backend
# se corre con `python -m app.main`, no con el CLI `uvicorn ...` directo).
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from fastapi import FastAPI  # noqa: E402
from fastapi.middleware.cors import CORSMiddleware  # noqa: E402

from app.api.chat import router as chat_router  # noqa: E402
from app.api.health import router as health_router  # noqa: E402
from app.core.config import settings  # noqa: E402

app = FastAPI(title="Kardex RAG API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router, prefix="/api")
app.include_router(chat_router, prefix="/api")

if __name__ == "__main__":
    import uvicorn

    # loop="none" evita que uvicorn hardcodee ProactorEventLoop en Windows
    # (lo hace incluso si ya fijamos la policy arriba) y deja que respete la
    # policy activa.
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.backend_port,
        reload=True,
        loop="none",
    )
