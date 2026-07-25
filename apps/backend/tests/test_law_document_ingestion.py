from carbonpilot.law_rag.documents import chunk_pages


def test_chunk_pages_preserves_page_and_paragraph_location():
    chunks = chunk_pages([(3, "a" * 1100)], size=1000, overlap=100)
    assert len(chunks) == 2
    assert chunks[0]["page_start"] == 3
    assert chunks[1]["paragraph_start"] == 1
    assert chunks[0]["text"][-100:] == chunks[1]["text"][:100]
