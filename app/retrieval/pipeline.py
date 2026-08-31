"""End-to-end retrieval pipeline."""

from __future__ import annotations

import time
from typing import Any

from app.core.config import RetrievalSettings
from app.domain import RetrievalTrace, ScoredDocument
from app.retrieval.compression import ContextCompressor
from app.retrieval.dense import DenseRetriever
from app.retrieval.hybrid import HybridRetriever
from app.retrieval.mmr import MMRSelector
from app.retrieval.multi_query import MultiQueryGenerator
from app.retrieval.neighbor_expansion import NeighborExpander
from app.retrieval.query_processor import QueryProcessor
from app.retrieval.query_rewriter import QueryRewriter
from app.retrieval.reranker import LexicalReranker, Reranker
from app.retrieval.sparse import SparseRetriever


class RetrievalPipeline:
    def __init__(
        self,
        settings: RetrievalSettings,
        dense: DenseRetriever,
        sparse: SparseRetriever,
        mmr: MMRSelector,
        neighbor_expander: NeighborExpander,
        reranker: Reranker | None = None,
        query_processor: QueryProcessor | None = None,
        query_rewriter: QueryRewriter | None = None,
        multi_query: MultiQueryGenerator | None = None,
        compressor: ContextCompressor | None = None,
    ) -> None:
        self.settings = settings
        self.dense = dense
        self.sparse = sparse
        self.hybrid = HybridRetriever(dense, sparse)
        self.mmr = mmr
        self.neighbor_expander = neighbor_expander
        self.reranker = reranker or LexicalReranker()
        self.query_processor = query_processor or QueryProcessor()
        self.query_rewriter = query_rewriter or QueryRewriter()
        self.multi_query = multi_query or MultiQueryGenerator()
        self.compressor = compressor or ContextCompressor()

    def retrieve(self, question: str, filters: dict[str, Any] | None = None) -> tuple[list[ScoredDocument], RetrievalTrace]:
        trace = RetrievalTrace(query=question)
        start = time.perf_counter()
        query = self.query_processor.process(question)
        trace.latency_ms["query_processing"] = _elapsed(start)

        rewritten = query
        if self.settings.enable_query_rewrite:
            stage = time.perf_counter()
            try:
                rewritten = self.query_rewriter.rewrite(query)
                trace.rewritten_query = rewritten
            except Exception as exc:
                trace.warnings.append(f"query_rewrite_failed: {exc}")
            trace.latency_ms["query_rewrite"] = _elapsed(stage)

        queries = self.multi_query.generate(rewritten) if self.settings.enable_multi_query else [rewritten]
        trace.queries = queries

        stage = time.perf_counter()
        candidates: list[ScoredDocument] = []
        for active_query in queries:
            try:
                if self.settings.enable_hybrid_search:
                    dense_results, sparse_results, fused = self.hybrid.retrieve(
                        active_query,
                        self.settings.dense_top_k,
                        self.settings.sparse_top_k,
                        self.settings.mmr_fetch_k,
                        filters,
                    )
                    trace.dense_results.extend([item.document.id for item in dense_results])
                    trace.sparse_results.extend([item.document.id for item in sparse_results])
                    candidates.extend(fused)
                else:
                    dense_results = self.dense.retrieve(active_query, self.settings.mmr_fetch_k, filters)
                    trace.dense_results.extend([item.document.id for item in dense_results])
                    candidates.extend(dense_results)
            except Exception as exc:
                trace.warnings.append(f"hybrid_retrieval_failed: {exc}")
                candidates.extend(self.dense.retrieve(active_query, self.settings.mmr_fetch_k, filters))
        candidates = _dedupe(candidates)
        trace.fused_results = [item.document.id for item in candidates]
        trace.latency_ms["retrieval"] = _elapsed(stage)

        if self.settings.enable_mmr:
            stage = time.perf_counter()
            try:
                candidates = self.mmr.select(rewritten, candidates, self.settings.top_k, self.settings.mmr_lambda)
            except Exception as exc:
                trace.warnings.append(f"mmr_failed: {exc}")
            trace.mmr_results = [item.document.id for item in candidates]
            trace.latency_ms["mmr"] = _elapsed(stage)

        if self.settings.enable_neighbor_expansion:
            stage = time.perf_counter()
            try:
                candidates = _dedupe(self.neighbor_expander.expand(candidates))
            except Exception as exc:
                trace.warnings.append(f"neighbor_expansion_failed: {exc}")
            trace.latency_ms["neighbor_expansion"] = _elapsed(stage)

        if self.settings.enable_reranker:
            stage = time.perf_counter()
            try:
                candidates = self.reranker.rerank(rewritten, candidates, self.settings.rerank_top_k)
            except Exception as exc:
                trace.warnings.append(f"rerank_failed: {exc}")
            trace.reranked_results = [item.document.id for item in candidates]
            trace.latency_ms["rerank"] = _elapsed(stage)

        if self.settings.enable_compression:
            stage = time.perf_counter()
            try:
                candidates = self.compressor.compress(rewritten, candidates, self.settings.context_max_chars)
            except Exception as exc:
                trace.warnings.append(f"compression_failed: {exc}")
            trace.latency_ms["compression"] = _elapsed(stage)

        trace.final_chunk_ids = [item.document.id for item in candidates]
        trace.latency_ms["total"] = _elapsed(start)
        return candidates, trace


def _dedupe(items: list[ScoredDocument]) -> list[ScoredDocument]:
    best: dict[str, ScoredDocument] = {}
    for item in items:
        current = best.get(item.document.id)
        if current is None or item.score > current.score:
            best[item.document.id] = item
    return sorted(best.values(), key=lambda item: item.score, reverse=True)


def _elapsed(start: float) -> float:
    return round((time.perf_counter() - start) * 1000, 3)
