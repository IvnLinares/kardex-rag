"""Cadena RAG: retriever (top-5, pgvector) + LLM restringido al contexto.

Incluye un guardrail por score de similitud: si el mejor resultado
recuperado esta lejos de la pregunta, se responde con un mensaje fijo sin
llamar al LLM. Un modelo chico como `phi3` no sigue de forma confiable la
instruccion "no respondas fuera de contexto" (ver CLAUDE.md, Dia 3) -- el
guardrail por score es mas confiable que depender solo del prompt.
"""

from collections.abc import AsyncIterator
from dataclasses import dataclass, field

from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama

from app.core.config import settings
from app.rag.vectorstore import get_vectorstore

SYSTEM_PROMPT = (
    "Eres un analista de inventarios experto. Respondes UNICAMENTE preguntas sobre "
    "el Kardex (productos, bodegas, cantidades, estados) usando EXCLUSIVAMENTE el "
    "CONTEXTO provisto abajo. Respondes en 1-3 oraciones, sin agregar preguntas ni "
    "secciones adicionales."
)

RETRIEVER_TOP_K = 5

# Distancia coseno (pgvector, menor = mas similar) maxima para considerar que
# hay contexto relevante. Calibrado empiricamente: preguntas dentro del
# dominio del Kardex puntuaron <=0.294, preguntas fuera de contexto (ej.
# "cual es la capital de Francia?") puntuaron >=0.329. Ver CLAUDE.md Dia 6.
RELEVANCE_THRESHOLD = 0.32

NO_CONTEXT_ANSWER = (
    "No tengo esa informacion en la base de datos del Kardex. Puedo responder "
    "preguntas sobre productos, bodegas, cantidades y estados de inventario."
)


@dataclass
class Source:
    producto_id: str
    nombre: str


def _to_sources(docs: list[Document]) -> list[Source]:
    return [
        Source(
            producto_id=str(doc.metadata.get("producto_id", "")),
            nombre=str(doc.metadata.get("nombre", "")),
        )
        for doc in docs
    ]


def format_docs(docs: list[Document]) -> str:
    if not docs:
        return "(sin resultados relevantes en la base de datos)"
    return "\n\n".join(f"- {doc.page_content}" for doc in docs)


def _build_prompt() -> ChatPromptTemplate:
    return ChatPromptTemplate.from_messages(
        [
            ("system", SYSTEM_PROMPT),
            ("human", "Contexto:\n{context}\n\nPregunta: {question}"),
        ]
    )


def _build_llm() -> ChatOllama:
    return ChatOllama(
        model=settings.ollama_model,
        base_url=settings.ollama_base_url,
        temperature=0,
        num_predict=200,
    )


@dataclass
class Answer:
    text: str
    sources: list[Source] = field(default_factory=list)
    in_context: bool = True


def answer_question(question: str) -> Answer:
    """Version sincrona (usada por la consola y los tests)."""
    vectorstore = get_vectorstore(async_mode=False)
    scored_docs = vectorstore.similarity_search_with_score(question, k=RETRIEVER_TOP_K)

    if not scored_docs or scored_docs[0][1] > RELEVANCE_THRESHOLD:
        return Answer(text=NO_CONTEXT_ANSWER, sources=[], in_context=False)

    docs = [doc for doc, _score in scored_docs]
    chain = _build_prompt() | _build_llm()
    result = chain.invoke({"context": format_docs(docs), "question": question})
    return Answer(text=str(result.content), sources=_to_sources(docs), in_context=True)


async def astream_answer(question: str) -> AsyncIterator[str | list[Source]]:
    """Version async (usada por /api/chat). Yieldea texto en chunks (str) y,
    al final, la lista de fuentes citadas (list[Source])."""
    vectorstore = get_vectorstore(async_mode=True)
    scored_docs = await vectorstore.asimilarity_search_with_score(question, k=RETRIEVER_TOP_K)

    if not scored_docs or scored_docs[0][1] > RELEVANCE_THRESHOLD:
        yield NO_CONTEXT_ANSWER
        yield []
        return

    docs = [doc for doc, _score in scored_docs]
    chain = _build_prompt() | _build_llm()
    async for chunk in chain.astream({"context": format_docs(docs), "question": question}):
        if chunk.content:
            yield str(chunk.content)
    yield _to_sources(docs)
