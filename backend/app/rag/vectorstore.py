from langchain_ollama import OllamaEmbeddings
from langchain_postgres import PGVector

from app.core.config import settings

COLLECTION_NAME = "kardex"


def get_embeddings() -> OllamaEmbeddings:
    return OllamaEmbeddings(
        model=settings.ollama_embedding_model,
        base_url=settings.ollama_base_url,
    )


def get_vectorstore(*, async_mode: bool = False) -> PGVector:
    return PGVector(
        embeddings=get_embeddings(),
        collection_name=COLLECTION_NAME,
        connection=settings.database_url_psycopg,
        use_jsonb=True,
        async_mode=async_mode,
    )
