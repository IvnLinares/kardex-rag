from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=("../.env", ".env"), extra="ignore")

    # URL de conexion "generica" (sin driver), ej: postgresql://user:pass@host:port/db
    database_url: str = "postgresql://kardex_admin:changeme@localhost:5433/kardex_rag"
    backend_port: int = 8000
    cors_origins: str = "http://localhost:5173"

    # NOTA: `llm_provider`/`openai_*` documentan la alternativa OpenAI (ver
    # CLAUDE.md secciones 3 y 8), pero app/rag/chain.py todavia usa ChatOllama
    # sin condicionar por `llm_provider` -- no estan conectados al codigo.
    llm_provider: str = "ollama"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "phi3"
    ollama_embedding_model: str = "nomic-embed-text"

    openai_api_key: str | None = None
    openai_model: str = "gpt-4o-mini"
    openai_embedding_model: str = "text-embedding-3-small"

    @property
    def _database_url_base(self) -> str:
        """`database_url` sin sufijo de driver, admite que ya venga con uno."""
        return self.database_url.replace("postgresql+asyncpg://", "postgresql://").replace(
            "postgresql+psycopg://", "postgresql://"
        )

    @property
    def database_url_asyncpg(self) -> str:
        """Para el engine async de SQLAlchemy (FastAPI)."""
        return self._database_url_base.replace("postgresql://", "postgresql+asyncpg://", 1)

    @property
    def database_url_psycopg(self) -> str:
        """Para el vectorstore sincrono de langchain-postgres."""
        return self._database_url_base.replace("postgresql://", "postgresql+psycopg://", 1)


settings = Settings()
