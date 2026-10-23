"""Local BGE embeddings. No hosted embedding API is required."""

from __future__ import annotations

from functools import lru_cache

import numpy as np
from fastembed import TextEmbedding

from app.config import EMBEDDING_BACKEND, EMBEDDING_MODEL_ID
from app.documents import chunk_text

# Official BGE retrieval prefix (sentence-transformers / FlagEmbedding).
# Applied to queries only. CV passages are embedded without it.
QUERY_PREFIX = "Represent this sentence for searching relevant passages: "


@lru_cache(maxsize=1)
def _model() -> TextEmbedding:
    # fastembed downloads an ONNX build of the Hugging Face model id
    # BAAI/bge-base-en-v1.5 (the same id sentence-transformers uses).
    return TextEmbedding(model_name=EMBEDDING_MODEL_ID)


def embedding_model_label() -> str:
    return f"{EMBEDDING_MODEL_ID} ({EMBEDDING_BACKEND})"


def _normalize(rows: list) -> list[list[float]]:
    vectors: list[list[float]] = []
    for row in rows:
        array = np.asarray(row, dtype=np.float32)
        norm = float(np.linalg.norm(array))
        if norm > 0:
            array = array / norm
        vectors.append(array.tolist())
    return vectors


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Embed CV passages. No query prefix."""
    if not texts:
        return []
    return _normalize(list(_model().passage_embed(texts)))


def embed_query(text: str, lead: str | None = None) -> list[float]:
    """Average query-chunk vectors so a long job description is not truncated.

    ``lead`` (usually the title and must-have skills) is blended in at a higher
    weight so later boilerplate does not drown the role. Each piece is prefixed
    the way BGE expects a retrieval query to be prefixed.
    """
    parts = chunk_text(text, size=700, overlap=80) or [text.strip()]
    parts = parts[:6]
    vectors = embed_texts([f"{QUERY_PREFIX}{part}" for part in parts])
    pooled = np.mean(np.asarray(vectors, dtype=np.float32), axis=0)
    if lead and lead.strip():
        lead_vec = np.asarray(embed_texts([f"{QUERY_PREFIX}{lead.strip()}"])[0], dtype=np.float32)
        pooled = (0.65 * lead_vec) + (0.35 * pooled)
    norm = float(np.linalg.norm(pooled))
    if norm > 0:
        pooled = pooled / norm
    return pooled.tolist()
