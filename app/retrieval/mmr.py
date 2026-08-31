"""Maximal Marginal Relevance selection."""

from __future__ import annotations

from app.domain import ScoredDocument
from app.indexing.embeddings import EmbeddingProvider, cosine_similarity


class MMRSelector:
    def __init__(self, embeddings: EmbeddingProvider) -> None:
        self.embeddings = embeddings

    def select(self, query: str, candidates: list[ScoredDocument], top_k: int, lambda_mult: float) -> list[ScoredDocument]:
        if len(candidates) <= top_k:
            return candidates
        query_vector = self.embeddings.embed_query(query)
        doc_vectors = {item.document.id: self.embeddings.embed_query(item.document.text) for item in candidates}
        selected: list[ScoredDocument] = []
        remaining = candidates[:]
        while remaining and len(selected) < top_k:
            best = max(
                remaining,
                key=lambda item: lambda_mult * cosine_similarity(query_vector, doc_vectors[item.document.id])
                - (1 - lambda_mult) * max(
                    [cosine_similarity(doc_vectors[item.document.id], doc_vectors[chosen.document.id]) for chosen in selected] or [0.0]
                ),
            )
            selected.append(best)
            remaining.remove(best)
        return selected
