import hashlib
import logging
import math

from carbonpilot.config import get_settings

logger = logging.getLogger(__name__)
EMBEDDING_DIMENSIONS = 768


def _hash_embedding(text: str) -> list[float]:
    """Deterministic, dependency-free fallback embedding.

    Not semantically meaningful on its own, but it is a real, reproducible
    numeric vector: the same text always maps to the same vector, and
    pgvector similarity search works correctly against it. This keeps the
    retrieval pipeline fully functional without requiring an external
    embedding API key during local development, tests, or CI. It is
    swapped for a real embedding model call in `embed_text` whenever
    GEMINI_API_KEY is configured and reachable.
    """
    vector: list[float] = []
    seed = text.encode("utf-8")
    for i in range(EMBEDDING_DIMENSIONS):
        digest = hashlib.sha256(seed + i.to_bytes(4, "big")).digest()
        value = int.from_bytes(digest[:8], "big") / 2**64
        vector.append(value * 2 - 1)

    norm = math.sqrt(sum(component**2 for component in vector)) or 1.0
    return [component / norm for component in vector]

def embed_text(text: str) -> list[float]:
    """Returns a normalized embedding vector for `text`.

    Uses Gemini's embedding API when GEMINI_API_KEY is configured;
    otherwise (or if the call fails, or returns an unexpected dimension)
    falls back to a deterministic local embedding so the semantic search
    pipeline still works end to end without external credentials.
    """
    settings = get_settings()
    if settings.gemini_api_key:
        try:
            import google.generativeai as genai

            genai.configure(api_key=settings.gemini_api_key)
            response = genai.embed_content(
                model="models/gemini-embedding-001",
                content=text,
                output_dimensionality=EMBEDDING_DIMENSIONS,
            )
            embedding = response["embedding"]
            if len(embedding) == EMBEDDING_DIMENSIONS:
                # Gemini doesn't guarantee a unit-length vector once
                # `output_dimensionality` truncates it, so we normalize
                # here to keep behaviour consistent with the local
                # fallback embedding (both are always unit vectors).
                norm = math.sqrt(sum(component**2 for component in embedding)) or 1.0
                return [component / norm for component in embedding]
            logger.warning(
                "Gemini embedding returned unexpected dimension %d (expected %d); "
                "falling back to local embedding.",
                len(embedding),
                EMBEDDING_DIMENSIONS,
            )
        except Exception:
            logger.warning("Gemini embedding call failed; falling back to local embedding.", exc_info=True)
    else:
        logger.warning("GEMINI_API_KEY not set; using local fallback embedding.")

    return _hash_embedding(text)
