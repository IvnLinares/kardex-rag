from app.rag.ingest import METADATA_COLUMNS, load_documents


def test_documents_have_content_and_metadata() -> None:
    documents = load_documents()

    assert len(documents) == 50
    for doc in documents:
        assert doc.page_content.strip(), "page_content vacio (revisar content_columns de CSVLoader)"
        for column in METADATA_COLUMNS:
            assert column in doc.metadata
