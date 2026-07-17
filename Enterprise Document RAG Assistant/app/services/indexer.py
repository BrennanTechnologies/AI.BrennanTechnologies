# Author:  Chris Brennan
# Company: Brennan Technologies, LLC
# Email:   chris@brennantechnologies.com
# Web:     https://www.brennantechnologies.com

from __future__ import annotations

from pathlib import Path
from typing import Iterable
from uuid import uuid4

from azure.search.documents import SearchClient
from openai import AzureOpenAI
from pypdf import PdfReader

from app.config import Settings


def _read_markdown(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def _read_pdf(path: Path) -> str:
    reader = PdfReader(str(path))
    parts: list[str] = []
    for page in reader.pages:
        parts.append(page.extract_text() or "")
    return "\n".join(parts)


def read_document(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".md":
        return _read_markdown(path)
    if suffix == ".pdf":
        return _read_pdf(path)
    raise ValueError(f"Unsupported file type: {suffix}")


def chunk_text(text: str, chunk_size: int, chunk_overlap: int) -> list[str]:
    cleaned = " ".join(text.split())
    if not cleaned:
        return []

    chunks: list[str] = []
    start = 0
    while start < len(cleaned):
        end = min(len(cleaned), start + chunk_size)
        chunks.append(cleaned[start:end])
        if end == len(cleaned):
            break
        start = max(0, end - chunk_overlap)
    return chunks


def _embed_texts(openai_client: AzureOpenAI, deployment: str, texts: Iterable[str]) -> list[list[float]]:
    text_list = list(texts)
    if not text_list:
        return []

    response = openai_client.embeddings.create(model=deployment, input=text_list)
    return [item.embedding for item in response.data]


def index_file(
    path: Path,
    search_client: SearchClient,
    openai_client: AzureOpenAI,
    settings: Settings,
) -> int:
    raw_text = read_document(path)
    chunks = chunk_text(raw_text, settings.chunk_size, settings.chunk_overlap)
    if not chunks:
        return 0

    vectors = _embed_texts(openai_client, settings.azure_openai_embedding_deployment, chunks)
    payload = []

    for idx, (chunk, vector) in enumerate(zip(chunks, vectors), start=1):
        payload.append(
            {
                "id": str(uuid4()),
                "filename": path.name,
                "chunk_id": f"{path.stem}-{idx}",
                "content": chunk,
                "content_vector": vector,
            }
        )

    search_client.upload_documents(payload)
    return len(payload)
