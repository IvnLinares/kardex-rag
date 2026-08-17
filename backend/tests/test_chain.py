from langchain_core.documents import Document

from app.rag.chain import Source, _to_sources, format_docs


def test_format_docs_joins_page_content() -> None:
    docs = [Document(page_content="a: 1"), Document(page_content="b: 2")]
    result = format_docs(docs)
    assert "a: 1" in result
    assert "b: 2" in result


def test_format_docs_empty_list() -> None:
    assert "sin resultados" in format_docs([])


def test_to_sources_extracts_metadata() -> None:
    docs = [Document(page_content="", metadata={"producto_id": "P-1", "nombre": "Router"})]
    assert _to_sources(docs) == [Source(producto_id="P-1", nombre="Router")]


def test_to_sources_empty_list() -> None:
    assert _to_sources([]) == []
