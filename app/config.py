"""Paths and environment for the talent-matching demo."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")

JOBS_DIR = ROOT / "data" / "jobs"
CVS_DIR = ROOT / "data" / "cvs"
GOLDEN_PATH = ROOT / "data" / "golden.json"
COLLECTION_NAME = "cvs"

# DeepSeek's public API is chat-only. This demo embeds locally with
# BAAI/bge-base-en-v1.5 (the sentence-transformers / Hugging Face id) via an
# ONNX build, so ingest does not need an OpenAI or DeepSeek embedding key.
DEFAULT_EMBEDDING_MODEL = "BAAI/bge-base-en-v1.5"
EMBEDDING_MODEL_ID = os.getenv("EMBEDDING_MODEL", DEFAULT_EMBEDDING_MODEL).strip() or (
    DEFAULT_EMBEDDING_MODEL
)
EMBEDDING_BACKEND = "local ONNX (fastembed)"

DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com").strip() or (
    "https://api.deepseek.com"
)
DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat").strip() or "deepseek-chat"

_PLACEHOLDER_KEYS = {
    "",
    "...",
    "changeme",
    "your-key",
    "your_api_key",
    "sk-xxx",
    "replace-me",
}


def chroma_dir() -> Path:
    raw = os.getenv("CHROMA_PATH", ".chroma").strip() or ".chroma"
    path = Path(raw)
    if not path.is_absolute():
        path = ROOT / path
    return path


def has_deepseek_key() -> bool:
    key = os.getenv("DEEPSEEK_API_KEY", "").strip()
    return key.lower() not in _PLACEHOLDER_KEYS and len(key) > 8


def deepseek_api_key() -> str:
    return os.getenv("DEEPSEEK_API_KEY", "").strip()
