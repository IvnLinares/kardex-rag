from langchain_core.documents import Document

from app.rag.chain import format_docs


def test_format_docs_joins_page_content() -> None:
    docs = [Document(page_content="a: 1"), Document(page_content="b: 2")]
    result = format_docs(docs)
    assert "a: 1" in result
    assert "b: 2" in result


def test_format_docs_empty_list() -> None:
    assert "sin resultados" in format_docs([])
