"""Rebuild the local Chroma index from data/jobs and data/cvs."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.config import CVS_DIR, JOBS_DIR, chroma_dir
from app.documents import all_chunks, load_jobs
from app.embeddings import embed_texts, embedding_model_label as model_label
from app.store import reset_collection


def ingest(jobs_dir: Path | None = None, cvs_dir: Path | None = None) -> dict:
    jobs = load_jobs(jobs_dir or JOBS_DIR)
    chunks = all_chunks(cvs_dir or CVS_DIR)
    embed_inputs = [f"{chunk.section}\n{chunk.text}" for chunk in chunks]
    vectors = embed_texts(embed_inputs)
    collection = reset_collection()
    batch = 64
    for start in range(0, len(chunks), batch):
        batch_chunks = chunks[start : start + batch]
        collection.add(
            ids=[chunk.chunk_id for chunk in batch_chunks],
            documents=[chunk.text for chunk in batch_chunks],
            embeddings=vectors[start : start + batch],
            metadatas=[
                {
                    "chunk_id": chunk.chunk_id,
                    "candidate_id": chunk.candidate_id,
                    "name": chunk.name,
                    "years_exp": int(chunk.years_exp),
                    "location": chunk.location,
                    "section": chunk.section,
                    "source_path": chunk.source_path,
                }
                for chunk in batch_chunks
            ],
        )
    return {
        "jobs": len(jobs),
        "cvs": len({chunk.candidate_id for chunk in chunks}),
        "chunks": len(chunks),
        "chroma_path": str(chroma_dir()),
        "embedding_model": model_label(),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Rebuild the Chroma CV index")
    parser.add_argument("--jobs-dir", type=Path, default=None)
    parser.add_argument("--cvs-dir", type=Path, default=None)
    args = parser.parse_args()
    summary = ingest(args.jobs_dir, args.cvs_dir)
    print(
        "Ingested {jobs} jobs, {cvs} CVs, {chunks} chunks".format(**summary)
    )
    print(f"Chroma: {summary['chroma_path']}")
    print(f"Embeddings: {summary['embedding_model']}")
    print("DeepSeek was not called. Ranking uses the API key only at match time.")


if __name__ == "__main__":
    main()
