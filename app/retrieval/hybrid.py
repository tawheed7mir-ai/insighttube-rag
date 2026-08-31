"""Hybrid retrieval."""

from __future__ import annotations

from typing import Any

from app.domain import ScoredDocument
from app.retrieval.dense import DenseRetriever
from app.retrieval.fusion import ReciprocalRankFusion
from app.retrieval.sparse import SparseRetriever


class HybridRetriever:
    def __init__(self, dense: DenseRetriever, sparse: SparseRetriever) -> None:
        self.dense = dense
        self.sparse = sparse
        self.fusion = ReciprocalRankFusion()

    def retrieve(
        self,
        query: str,
        dense_top_k: int,
        sparse_top_k: int,
        top_k: int,
        filters: dict[str, Any] | None = None,
    ) -> tuple[list[ScoredDocument], list[ScoredDocument], list[ScoredDocument]]:
        dense_results = self.dense.retrieve(query, dense_top_k, filters)
        sparse_results = self.sparse.retrieve(query, sparse_top_k, filters)
        fused = self.fusion.fuse([dense_results, sparse_results], top_k=top_k)
        return dense_results, sparse_results, fused
