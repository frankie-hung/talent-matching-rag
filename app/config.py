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

# DeepSeek's public API is chat-only. This demo embeds locally with the same
# MiniLM checkpoint sentence-transformers publishes, via Chroma's ONNX build,
# so ingest does not need an OpenAI (or DeepSeek) embedding key.
EMBEDDING_MODEL_ID = os.getenv(
    "EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2"
).strip() or "sentence-transformers/all-MiniLM-L6-v2"
EMBEDDING_BACKEND = "local ONNX (Chroma ONNXMiniLM_L6_V2)"

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
