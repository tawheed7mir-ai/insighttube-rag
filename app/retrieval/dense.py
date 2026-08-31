"""Dense retriever."""

from __future__ import annotations

from typing import Any

from app.domain import ScoredDocument
from app.indexing.embeddings import EmbeddingProvider
from app.indexing.vector_store import VectorStore


class DenseRetriever:
    def __init__(self, embeddings: EmbeddingProvider, vector_store: VectorStore) -> None:
        self.embeddings = embeddings
        self.vector_store = vector_store

    def retrieve(self, query: str, top_k: int, filters: dict[str, Any] | None = None) -> list[ScoredDocument]:
        return self.vector_store.search(self.embeddings.embed_query(query), top_k=top_k, filters=filters)
