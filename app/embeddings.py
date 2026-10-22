"""Local MiniLM embeddings. No hosted embedding API is required."""

from __future__ import annotations

from functools import lru_cache

import numpy as np
from chromadb.utils.embedding_functions import ONNXMiniLM_L6_V2

from app.config import EMBEDDING_BACKEND, EMBEDDING_MODEL_ID
from app.documents import chunk_text


@lru_cache(maxsize=1)
def _function() -> ONNXMiniLM_L6_V2:
    # Same checkpoint family as sentence-transformers/all-MiniLM-L6-v2.
    # Chroma ships an ONNX build so this demo does not install PyTorch.
    return ONNXMiniLM_L6_V2()


def embedding_model_label() -> str:
    return f"{EMBEDDING_MODEL_ID} ({EMBEDDING_BACKEND})"


def embed_texts(texts: list[str]) -> list[list[float]]:
    if not texts:
        return []
    raw = _function()(texts)
    vectors: list[list[float]] = []
    for row in raw:
        array = np.asarray(row, dtype=np.float32)
        norm = float(np.linalg.norm(array))
        if norm > 0:
            array = array / norm
        vectors.append(array.tolist())
    return vectors


def embed_query(text: str, lead: str | None = None) -> list[float]:
    """Average chunk vectors so a long job description is not truncated to 256 tokens.

    ``lead`` (usually the title and must-have skills) is blended in at a higher
    weight so later boilerplate does not drown the role.
    """
    parts = chunk_text(text, size=700, overlap=80) or [text.strip()]
    parts = parts[:6]
    vectors = embed_texts(parts)
    pooled = np.mean(np.asarray(vectors, dtype=np.float32), axis=0)
    if lead and lead.strip():
        lead_vec = np.asarray(embed_texts([lead.strip()])[0], dtype=np.float32)
        pooled = (0.65 * lead_vec) + (0.35 * pooled)
    norm = float(np.linalg.norm(pooled))
    if norm > 0:
        pooled = pooled / norm
    return pooled.tolist()
