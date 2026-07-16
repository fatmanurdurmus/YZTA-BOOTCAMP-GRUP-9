import math

from carbonpilot.law_rag.embeddings import EMBEDDING_DIMENSIONS, embed_text
from carbonpilot.law_rag.seed_data import CBAM_LAW_CHUNKS
from carbonpilot.schemas.law import LawReference


def test_embed_text_is_deterministic_and_normalized():
    first = embed_text("CBAM embedded emissions")
    second = embed_text("CBAM embedded emissions")

    assert first == second
    assert len(first) == EMBEDDING_DIMENSIONS

    norm = math.sqrt(sum(component**2 for component in first))
    assert math.isclose(norm, 1.0, rel_tol=1e-6)


def test_embed_text_differs_for_different_inputs():
    first = embed_text("CBAM embedded emissions")
    second = embed_text("GHG Protocol Scope 3")

    assert first != second


def test_seed_data_has_valid_law_reference_shape():
    assert len(CBAM_LAW_CHUNKS) >= 5

    for chunk in CBAM_LAW_CHUNKS:
        # Reuses LawReference's own validation (min lengths, valid URL) to
        # make sure every seeded chunk would also be usable as a LawReference.
        LawReference(
            title=chunk["title"],
            jurisdiction=chunk["jurisdiction"],
            url=chunk["source_url"],
            relevance=chunk["chunk_text"][:200],
            source_type="indexed_law_chunk",
        )
        assert len(chunk["chunk_text"]) > 50