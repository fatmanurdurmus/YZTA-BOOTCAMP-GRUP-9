"""Ingestion and chunking of user-uploaded legal documents."""

import hashlib

from sqlalchemy.orm import Session

from carbonpilot.config import get_settings
from carbonpilot.db import models
from carbonpilot.ingestion.documents import extract_document_text
from carbonpilot.ingestion.extractor import ProviderUnavailable
from carbonpilot.law_rag.embeddings import embed_text


def chunk_pages(pages: list[tuple[int, str]], size: int = 1000, overlap: int = 150) -> list[dict[str, object]]:
    chunks: list[dict[str, object]] = []
    paragraph = 0
    for page, text in pages:
        cleaned = text.strip()
        if not cleaned:
            continue
        paragraph += 1
        start = 0
        while start < len(cleaned):
            end = min(len(cleaned), start + size)
            chunks.append({"text": cleaned[start:end], "page_start": page, "page_end": page, "paragraph_start": paragraph, "paragraph_end": paragraph})
            if end == len(cleaned):
                break
            start = end - overlap
    return chunks


def ingest_law_document(*, db: Session, content: bytes, content_type: str, filename: str, title: str, jurisdiction: str, source_url: str) -> tuple[str, int]:
    if not get_settings().gemini_api_key:
        raise ProviderUnavailable("GEMINI_API_KEY is required for Law-RAG ingestion")
    digest = hashlib.sha256(content).hexdigest()
    existing = db.query(models.LawDocument).filter_by(content_hash=digest).one_or_none()
    if existing:
        return str(existing.id), 0
    document = models.LawDocument(title=title, jurisdiction=jurisdiction, source_url=source_url, file_name=filename, content_hash=digest)
    db.add(document)
    db.flush()
    pages = extract_document_text(content, content_type, filename)
    chunks = chunk_pages(pages)
    for chunk in chunks:
        db.add(models.LawChunk(law_document_id=document.id, title=title, jurisdiction=jurisdiction, source_url=source_url, chunk_text=str(chunk["text"]), embedding=embed_text(str(chunk["text"])), page_start=int(chunk["page_start"]), page_end=int(chunk["page_end"]), paragraph_start=int(chunk["paragraph_start"]), paragraph_end=int(chunk["paragraph_end"])))
    db.commit()
    return str(document.id), len(chunks)
