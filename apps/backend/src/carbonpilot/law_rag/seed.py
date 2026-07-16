from sqlalchemy.orm import Session

from carbonpilot.db import models
from carbonpilot.law_rag.embeddings import embed_text
from carbonpilot.law_rag.seed_data import CBAM_LAW_CHUNKS


def seed_law_chunks(db: Session) -> int:
    """Inserts the curated CBAM/SKDM law chunks into `law_chunks`, skipping
    any title that's already present so this can be run repeatedly without
    creating duplicates. Returns how many new rows were inserted.
    """
    inserted = 0
    for chunk in CBAM_LAW_CHUNKS:
        exists = db.query(models.LawChunk).filter_by(title=chunk["title"]).one_or_none()
        if exists is not None:
            continue

        db.add(
            models.LawChunk(
                title=chunk["title"],
                jurisdiction=chunk["jurisdiction"],
                source_url=chunk["source_url"],
                chunk_text=chunk["chunk_text"],
                embedding=embed_text(chunk["chunk_text"]),
            )
        )
        inserted += 1

    db.commit()
    return inserted