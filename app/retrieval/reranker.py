"""Reranking with optional CrossEncoder and deterministic fallback."""

from __future__ import annotations

from app.domain import ScoredDocument


class Reranker:
    def rerank(self, query: str, documents: list[ScoredDocument], top_k: int) -> list[ScoredDocument]: ...


class LexicalReranker:
    def rerank(self, query: str, documents: list[ScoredDocument], top_k: int) -> list[ScoredDocument]:
        terms = set(query.lower().split())
        reranked: list[ScoredDocument] = []
        for item in documents:
            overlap = len(terms.intersection(item.document.text.lower().split()))
            item.rerank_score = float(overlap) + item.score
            reranked.append(item)
        return sorted(reranked, key=lambda item: item.rerank_score or item.score, reverse=True)[:top_k]


class CrossEncoderReranker:
    def __init__(self, model_name: str) -> None:
        from sentence_transformers import CrossEncoder
        self.model = CrossEncoder(model_name)

    def rerank(self, query: str, documents: list[ScoredDocument], top_k: int) -> list[ScoredDocument]:
        pairs = [[query, item.document.text] for item in documents]
        scores = self.model.predict(pairs)
        for item, score in zip(documents, scores):
            item.rerank_score = float(score)
        return sorted(documents, key=lambda item: item.rerank_score or item.score, reverse=True)[:top_k]
