-- Se ejecuta automáticamente la primera vez que se crea el volumen de Postgres
-- (docker-entrypoint-initdb.d). Si el volumen ya existe, correr manualmente:
-- docker exec -it kardex_rag_db psql -U kardex_admin -d kardex_rag -f /docker-entrypoint-initdb.d/init.sql

CREATE EXTENSION IF NOT EXISTS vector;

-- No se crea una tabla manual para los embeddings: el vectorstore de LangChain
-- (langchain-postgres, ver backend/app/rag/ingest.py) gestiona su propio esquema
-- (langchain_pg_collection / langchain_pg_embedding) con la dimensión que
-- corresponda al modelo de embeddings configurado.
