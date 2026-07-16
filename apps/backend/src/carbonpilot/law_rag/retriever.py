from sqlalchemy import select
from sqlalchemy.orm import Session

from carbonpilot.db import models
from carbonpilot.law_rag.embeddings import embed_text
from carbonpilot.schemas.law import LawReference

def retrieve_default_references() -> list[LawReference]:
    return [
        LawReference(
            title="European Commission Carbon Border Adjustment Mechanism",
            jurisdiction="EU",
            url="https://taxation-customs.ec.europa.eu/carbon-border-adjustment-mechanism_en",
            relevance="CBAM scope, transition to definitive regime, reporting context.",
            source_type="official_guidance",
        ),
        LawReference(
            title="GHG Protocol Corporate Standard",
            jurisdiction="Global",
            url="https://ghgprotocol.org/corporate-standard",
            relevance="Scope 1, Scope 2, and Scope 3 accounting concepts.",
            source_type="standard",
        ),
    ]

def semantic_search(db: Session, query: str, top_k: int = 3) -> list[LawReference]:
    """CP-35: real pgvector-backed semantic search over the indexed CBAM/SKDM
    law chunks in the `law_chunks` table (seeded via `law_rag.seed`).

    Never raises: if the table hasn't been seeded yet, or the database is
    unavailable, this returns an empty list so callers can fall back to
    `retrieve_default_references()` on their own terms.
    """
    try:
        query_embedding = embed_text(query)
        rows = (
            db.execute(
                select(models.LawChunk)
                .order_by(models.LawChunk.embedding.cosine_distance(query_embedding))
                .limit(top_k)
            )
            .scalars()
            .all()
        )
    except Exception:
        return []

    return [
        LawReference(
            title=row.title,
            jurisdiction=row.jurisdiction,
            url=row.source_url,
            relevance=row.chunk_text[:200],
            source_type="indexed_law_chunk",
        )
        for row in rows
    ]
