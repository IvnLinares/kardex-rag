"""Cadena RAG: retriever (top-5, pgvector) + LLM restringido al contexto."""

from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.retrievers import BaseRetriever
from langchain_core.runnables import Runnable, RunnablePassthrough
from langchain_ollama import ChatOllama

from app.core.config import settings
from app.rag.vectorstore import get_vectorstore

SYSTEM_PROMPT = (
    "Eres un analista de inventarios experto. Respondes UNICAMENTE preguntas sobre "
    "el Kardex (productos, bodegas, cantidades, estados) usando EXCLUSIVAMENTE el "
    "CONTEXTO provisto abajo. Si la pregunta no tiene relacion con el inventario, o "
    "el CONTEXTO no tiene informacion suficiente para responderla, decis "
    "explicitamente que no tenes esa informacion en la base de datos: NUNCA "
    "respondas con conocimiento general ni inventes datos. Respondes en 1-3 "
    "oraciones, sin agregar preguntas ni secciones adicionales."
)

RETRIEVER_TOP_K = 5


def get_retriever() -> BaseRetriever:
    vectorstore = get_vectorstore()
    return vectorstore.as_retriever(search_kwargs={"k": RETRIEVER_TOP_K})


def format_docs(docs: list[Document]) -> str:
    if not docs:
        return "(sin resultados relevantes en la base de datos)"
    return "\n\n".join(f"- {doc.page_content}" for doc in docs)


def build_chain() -> Runnable:
    retriever = get_retriever()
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", SYSTEM_PROMPT),
            ("human", "Contexto:\n{context}\n\nPregunta: {question}"),
        ]
    )
    llm = ChatOllama(
        model=settings.ollama_model,
        base_url=settings.ollama_base_url,
        temperature=0,
        num_predict=200,
    )

    return (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )


def answer_question(question: str) -> str:
    chain = build_chain()
    return chain.invoke(question)
