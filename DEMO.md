# Guion para el video demo (Día 7)

Guion corto para grabar la demo del sprint. Pensado para ~3-4 minutos.

## Antes de grabar

```bash
docker compose up -d --build
```

Esperá a que los 4 contenedores estén arriba (`docker compose ps`, todos
`Up`/`healthy`) y confirmá que los modelos de Ollama ya están descargados
(si no, ver README sección "Infraestructura"):

```bash
docker exec -it kardex_rag_ollama ollama list
# deberia listar phi3 y nomic-embed-text
```

Si la colección `kardex` está vacía o querés datos frescos:

```bash
cd backend && python -m app.rag.ingest
```

Abrí **http://localhost:5173** en el navegador antes de empezar a grabar.

## Guion

1. **Mostrar el problema (10s).** "Este es un copiloto de IA para un sistema
   de inventarios: en vez de navegar tablas y filtros, se le pregunta en
   lenguaje natural."

2. **Pregunta dentro de contexto — streaming (30s).**
   Escribir: `¿Qué productos están agotados?`
   Señalar: el texto aparece progresivamente (no todo junto), y los nombres
   de los productos citados quedan resaltados en la respuesta.

3. **Segunda pregunta dentro de contexto (20s).**
   Escribir: `¿Cuánto stock hay de Router WiFi 6 y en qué bodega está?`
   Señalar: la respuesta usa datos reales del CSV (160 unidades, Bodega
   Central), no inventados.

4. **Anti-alucinación — pregunta fuera de contexto (20s).**
   Escribir: `¿Cuál es la capital de Francia?`
   Señalar: se niega a responder ("No tengo esa información en la base de
   datos del Kardex...") en vez de contestar con conocimiento general. Esto
   es un guardrail por score de similitud, no solo una instrucción al LLM
   (mencionar que un modelo chico como `phi3` no seguía esa instrucción de
   forma confiable — ver `backend/app/rag/chain.py` para el detalle técnico).

5. **Arquitectura, brevemente (40s).** Mostrar en el editor (o mencionar):
   - `docker-compose.yml`: 4 servicios (Postgres+pgvector, Ollama, FastAPI,
     Vue) — todo corre local, sin dependencias externas ni costos de API.
   - `backend/app/rag/ingest.py`: CSV → embeddings locales → pgvector.
   - `backend/app/rag/chain.py`: retriever top-5 + guardrail por score +
     LLM restringido al contexto.
   - `backend/app/api/chat.py`: streaming por Server-Sent Events.
   - `frontend/src/composables/useChat.ts`: consumo del streaming en Vue.

6. **CI y calidad (10s, opcional).** Mostrar el repo en GitHub: badge/checks
   verdes en Actions, `README.md` con el roadmap de los 7 días completo.

7. **Cierre (10s).** "Sprint de 7 días completo: infraestructura, ingesta de
   datos, cadena RAG, API con streaming, UI de chat, y control de
   alucinaciones."

## Preguntas de respaldo (por si alguna falla en vivo)

- `¿Qué hay en la Bodega Norte?`
- `Productos de la categoría limpieza`
- `Estado del Taladro percutor`
- `Escribime un poema sobre el otoño` (fuera de contexto, otra variante)

## Al terminar

```bash
docker compose down
```
