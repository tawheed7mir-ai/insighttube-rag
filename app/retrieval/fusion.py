"""Candidate fusion utilities."""

from __future__ import annotations

from app.domain import ScoredDocument


class ReciprocalRankFusion:
    def fuse(self, result_sets: list[list[ScoredDocument]], top_k: int, k: int = 60) -> list[ScoredDocument]:
        scores: dict[str, float] = {}
        docs: dict[str, ScoredDocument] = {}
        sources: dict[str, set[str]] = {}
        for results in result_sets:
            for rank, item in enumerate(results, start=1):
                doc_id = item.document.id
                scores[doc_id] = scores.get(doc_id, 0.0) + 1.0 / (k + rank)
                docs[doc_id] = item
                sources.setdefault(doc_id, set()).add(item.source)
        fused = [
            ScoredDocument(document=docs[doc_id].document, score=score, source="+".join(sorted(sources[doc_id])))
            for doc_id, score in scores.items()
        ]
        return sorted(fused, key=lambda item: item.score, reverse=True)[:top_k]
