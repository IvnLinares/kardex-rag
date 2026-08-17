-- Se ejecuta automáticamente la primera vez que se crea el volumen de Postgres
-- (docker-entrypoint-initdb.d). Si el volumen ya existe, correr manualmente:
-- docker exec -it kardex_rag_db psql -U kardex_admin -d kardex_rag -f /docker-entrypoint-initdb.d/init.sql

CREATE EXTENSION IF NOT EXISTS vector;

-- Tabla base para los embeddings del Kardex (referencia inicial, LangChain puede
-- crear su propia tabla de vectorstore; ajustar en Día 2 según el loader elegido).
CREATE TABLE IF NOT EXISTS kardex_embeddings (
    id SERIAL PRIMARY KEY,
    producto_id TEXT NOT NULL,
    contenido TEXT NOT NULL,
    metadata JSONB,
    embedding VECTOR(1536),
    created_at TIMESTAMPTZ DEFAULT now()
);
