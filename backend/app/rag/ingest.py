"""Ingesta del CSV de Kardex hacia pgvector.

Uso (desde /backend, con el venv activado):
    python -m app.rag.ingest
"""

import logging
from pathlib import Path

from langchain_community.document_loaders import CSVLoader
from langchain_ollama import OllamaEmbeddings
from langchain_postgres import PGVector

from app.core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CSV_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "kardex.csv"
COLLECTION_NAME = "kardex"

METADATA_COLUMNS = [
    "producto_id",
    "nombre",
    "categoria",
    "bodega",
    "cantidad",
    "fecha_ultimo_movimiento",
    "estado",
]


def load_documents() -> list:
    loader = CSVLoader(
        file_path=str(CSV_PATH),
        encoding="utf-8",
        metadata_columns=METADATA_COLUMNS,
        content_columns=METADATA_COLUMNS,
    )
    return loader.load()


def main() -> None:
    if not CSV_PATH.exists():
        raise FileNotFoundError(f"No se encontro el CSV de Kardex en {CSV_PATH}")

    documents = load_documents()
    logger.info("Cargados %d documentos desde %s", len(documents), CSV_PATH)

    embeddings = OllamaEmbeddings(
        model=settings.ollama_embedding_model,
        base_url=settings.ollama_base_url,
    )

    vectorstore = PGVector(
        embeddings=embeddings,
        collection_name=COLLECTION_NAME,
        connection=settings.database_url_psycopg,
        use_jsonb=True,
        pre_delete_collection=True,
    )
    ids = vectorstore.add_documents(documents)
    logger.info("Ingesta completa: %d vectores en la coleccion '%s'", len(ids), COLLECTION_NAME)


if __name__ == "__main__":
    main()
