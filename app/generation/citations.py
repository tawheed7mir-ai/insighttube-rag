"""Citation extraction from retrieved chunks."""

from __future__ import annotations

from app.domain import Citation, ScoredDocument


class CitationBuilder:
    def build(self, documents: list[ScoredDocument]) -> list[Citation]:
        citations: list[Citation] = []
        for item in documents:
            metadata = item.document.metadata
            citations.append(
                Citation(
                    chunk_id=item.document.id,
                    video_id=str(metadata.get("video_id", "")),
                    start_timestamp=str(metadata.get("start_timestamp", "")),
                    end_timestamp=str(metadata.get("end_timestamp", "")),
                    url=str(metadata.get("source_url", "")),
                    text=item.document.text[:300],
                    score=item.rerank_score if item.rerank_score is not None else item.score,
                )
            )
        return citations
