"""Load job and CV files, then split CVs into grounded chunks."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from app.config import CVS_DIR, JOBS_DIR, ROOT

_FRONTMATTER = re.compile(r"^---\s*\n(.*?)\n---\s*\n?", re.DOTALL)
_HEADING = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)


@dataclass
class Job:
    job_id: str
    title: str
    location: str
    years_required: int
    must_have_skills: list[str]
    body: str
    source_path: str

    def embedding_lead(self) -> str:
        skills = ", ".join(self.must_have_skills)
        return f"{self.title}. Must-have skills: {skills}"

    def query_text(self) -> str:
        return (
            f"{self.embedding_lead()}\n"
            f"Location: {self.location}\n"
            f"Minimum years: {self.years_required}\n\n"
            f"{self.body}"
        )


@dataclass
class CvDocument:
    candidate_id: str
    name: str
    years_exp: int
    location: str
    body: str
    source_path: str


@dataclass
class CvChunk:
    chunk_id: str
    candidate_id: str
    name: str
    years_exp: int
    location: str
    section: str
    text: str
    source_path: str


def repo_relative(path: Path) -> str:
    resolved = path.resolve()
    try:
        return resolved.relative_to(ROOT).as_posix()
    except ValueError:
        return resolved.as_posix()


def split_frontmatter(text: str) -> tuple[dict, str]:
    match = _FRONTMATTER.match(text)
    if not match:
        return {}, text.strip()
    loaded = yaml.safe_load(match.group(1)) or {}
    if not isinstance(loaded, dict):
        raise ValueError("Frontmatter must be a mapping")
    return loaded, text[match.end() :].strip()


def read_text(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        from pypdf import PdfReader

        reader = PdfReader(str(path))
        pages = [(page.extract_text() or "") for page in reader.pages]
        return "\n\n".join(pages).strip()
    return path.read_text(encoding="utf-8")


def chunk_text(text: str, size: int = 800, overlap: int = 120) -> list[str]:
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    if not text:
        return []
    if len(text) <= size:
        return [text]
    parts: list[str] = []
    start = 0
    while start < len(text):
        end = min(len(text), start + size)
        if end < len(text):
            cut = text.rfind("\n", start + size // 2, end)
            if cut == -1:
                cut = text.rfind(" ", start + size // 2, end)
            if cut != -1:
                end = cut
        piece = text[start:end].strip()
        if piece:
            parts.append(piece)
        if end >= len(text):
            break
        next_start = end - overlap
        if next_start <= start:
            next_start = end
        start = next_start
    return parts


def section_blocks(body: str) -> list[tuple[str, str]]:
    matches = list(_HEADING.finditer(body))
    if not matches:
        cleaned = body.strip()
        return [("Body", cleaned)] if cleaned else []
    blocks: list[tuple[str, str]] = []
    preamble = body[: matches[0].start()].strip()
    if preamble:
        blocks.append(("Preamble", preamble))
    for index, match in enumerate(matches):
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(body)
        title = match.group(1).strip() or "Section"
        content = body[start:end].strip()
        if content:
            blocks.append((title, content))
    return blocks


def _slug(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.casefold()).strip("-")
    return slug or "section"


def _as_int(value: object, default: int = 0) -> int:
    if value is None or value == "":
        return default
    try:
        return int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Expected an integer, got {value!r}") from exc


def load_job(path: Path) -> Job:
    meta, body = split_frontmatter(read_text(path))
    skills = meta.get("must_have_skills") or []
    if isinstance(skills, str):
        skills = [skills]
    if not isinstance(skills, list):
        raise ValueError(f"{path}: must_have_skills must be a list")
    title = str(meta.get("title") or path.stem)
    return Job(
        job_id=str(meta.get("job_id") or path.stem),
        title=title,
        location=str(meta.get("location") or ""),
        years_required=_as_int(meta.get("years_required"), 0),
        must_have_skills=[str(item) for item in skills],
        body=body,
        source_path=repo_relative(path),
    )


def load_jobs(directory: Path | None = None) -> list[Job]:
    folder = directory or JOBS_DIR
    paths = sorted(folder.glob("*.md"))
    if not paths:
        raise FileNotFoundError(f"No job files in {folder}")
    jobs = [load_job(path) for path in paths]
    ids = [job.job_id for job in jobs]
    if len(ids) != len(set(ids)):
        raise ValueError(f"Duplicate job_id values in {folder}")
    return jobs


def load_cv(path: Path) -> CvDocument:
    meta, body = split_frontmatter(read_text(path))
    if not body:
        raise ValueError(f"{path} has no résumé text")
    candidate_id = str(meta.get("candidate_id") or path.stem)
    name = str(meta.get("name") or candidate_id)
    return CvDocument(
        candidate_id=candidate_id,
        name=name,
        years_exp=_as_int(meta.get("years_exp"), 0),
        location=str(meta.get("location") or "Unknown"),
        body=body,
        source_path=repo_relative(path),
    )


def iter_cv_paths(directory: Path | None = None) -> list[Path]:
    folder = directory or CVS_DIR
    paths: list[Path] = []
    for pattern in ("*.md", "*.txt", "*.pdf"):
        paths.extend(folder.glob(pattern))
    return sorted(paths)


def load_cvs(directory: Path | None = None) -> list[CvDocument]:
    paths = iter_cv_paths(directory)
    if not paths:
        raise FileNotFoundError(f"No CV files in {directory or CVS_DIR}")
    documents = [load_cv(path) for path in paths]
    ids = [doc.candidate_id for doc in documents]
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate candidate_id values")
    return documents


def chunks_for_cv(document: CvDocument) -> list[CvChunk]:
    chunks: list[CvChunk] = []
    for section, content in section_blocks(document.body):
        for index, piece in enumerate(chunk_text(content)):
            chunks.append(
                CvChunk(
                    chunk_id=f"{document.candidate_id}:{_slug(section)}:{index}",
                    candidate_id=document.candidate_id,
                    name=document.name,
                    years_exp=document.years_exp,
                    location=document.location,
                    section=section,
                    text=piece,
                    source_path=document.source_path,
                )
            )
    if not chunks:
        raise ValueError(f"No chunks produced for {document.candidate_id}")
    return chunks


def all_chunks(directory: Path | None = None) -> list[CvChunk]:
    chunks: list[CvChunk] = []
    for document in load_cvs(directory):
        chunks.extend(chunks_for_cv(document))
    return chunks


@dataclass
class LoadedCorpus:
    jobs: list[Job] = field(default_factory=list)
    chunks: list[CvChunk] = field(default_factory=list)
