"""Sparse retriever wrapper."""

from __future__ import annotations

from typing import Any

from app.domain import ScoredDocument
from app.indexing.sparse_index import BM25Index


class SparseRetriever:
    def __init__(self, index: BM25Index) -> None:
        self.index = index

    def retrieve(self, query: str, top_k: int, filters: dict[str, Any] | None = None) -> list[ScoredDocument]:
        return self.index.search(query, top_k=top_k, filters=filters)
