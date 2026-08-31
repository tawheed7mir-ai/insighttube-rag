"""Neighbor chunk expansion."""

from __future__ import annotations

from app.domain import ScoredDocument
from app.indexing.vector_store import VectorStore


class NeighborExpander:
    def __init__(self, vector_store: VectorStore) -> None:
        self.vector_store = vector_store

    def expand(self, documents: list[ScoredDocument]) -> list[ScoredDocument]:
        seen = {item.document.id for item in documents}
        expanded = documents[:]
        for item in documents:
            for key in ("previous_chunk_id", "next_chunk_id"):
                neighbor_id = item.document.metadata.get(key)
                if neighbor_id and neighbor_id not in seen:
                    neighbor = self.vector_store.get(neighbor_id)
                    if neighbor:
                        expanded.append(ScoredDocument(document=neighbor, score=item.score * 0.8, source="neighbor"))
                        seen.add(neighbor_id)
        return expanded
