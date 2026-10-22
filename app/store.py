"""Persistent Chroma collection of CV chunks."""

from __future__ import annotations

from functools import lru_cache

import chromadb

from app.config import COLLECTION_NAME, chroma_dir


@lru_cache(maxsize=1)
def get_client() -> chromadb.PersistentClient:
    path = chroma_dir()
    path.mkdir(parents=True, exist_ok=True)
    return chromadb.PersistentClient(path=str(path))


def reset_collection() -> chromadb.Collection:
    client = get_client()
    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        # Missing collection on first ingest is expected.
        pass
    return client.create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )


def get_collection() -> chromadb.Collection:
    try:
        return get_client().get_collection(COLLECTION_NAME)
    except Exception as exc:
        raise RuntimeError(
            "No CV index found. From the repo root run: python -m app.ingest"
        ) from exc


def index_count() -> int:
    try:
        return get_collection().count()
    except RuntimeError:
        return 0
