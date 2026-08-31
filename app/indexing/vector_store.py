"""JSON-backed vector store abstraction for local development."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Protocol

from app.domain import Document, ScoredDocument
from app.indexing.embeddings import EmbeddingProvider, cosine_similarity


class VectorStore(Protocol):
    def upsert(self, documents: list[Document], vectors: list[list[float]]) -> None: ...
    def search(self, query_vector: list[float], top_k: int, filters: dict[str, Any] | None = None) -> list[ScoredDocument]: ...
    def get(self, document_id: str) -> Document | None: ...
    def all_documents(self) -> list[Document]: ...


class JsonVectorStore:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._items: dict[str, dict[str, Any]] = {}
        self._load()

    def _load(self) -> None:
        if self.path.exists():
            self._items = json.loads(self.path.read_text(encoding="utf-8"))

    def _persist(self) -> None:
        self.path.write_text(json.dumps(self._items, indent=2), encoding="utf-8")

    def upsert(self, documents: list[Document], vectors: list[list[float]]) -> None:
        for document, vector in zip(documents, vectors):
            existing = self._items.get(document.id)
            if existing and existing["document"]["metadata"].get("content_hash") == document.metadata.get("content_hash"):
                continue
            self._items[document.id] = {"document": _dump(document), "vector": vector}
        self._persist()

    def search(self, query_vector: list[float], top_k: int, filters: dict[str, Any] | None = None) -> list[ScoredDocument]:
        results: list[ScoredDocument] = []
        for item in self._items.values():
            document = Document(**item["document"])
            if not _matches(document.metadata, filters):
                continue
            score = cosine_similarity(query_vector, item["vector"])
            results.append(ScoredDocument(document=document, score=score, source="dense"))
        return sorted(results, key=lambda item: item.score, reverse=True)[:top_k]

    def get(self, document_id: str) -> Document | None:
        item = self._items.get(document_id)
        return Document(**item["document"]) if item else None

    def all_documents(self) -> list[Document]:
        return [Document(**item["document"]) for item in self._items.values()]


def build_documents_from_chunks(chunks: list[Any]) -> list[Document]:
    return [Document(id=chunk.chunk_id, text=chunk.text, metadata=chunk.to_document_metadata()) for chunk in chunks]


def _matches(metadata: dict[str, Any], filters: dict[str, Any] | None) -> bool:
    if not filters:
        return True
    for key, value in filters.items():
        if value is not None and metadata.get(key) != value:
            return False
    return True


def _dump(model: Document) -> dict[str, Any]:
    if hasattr(model, "model_dump"):
        return model.model_dump()
    return model.dict()
