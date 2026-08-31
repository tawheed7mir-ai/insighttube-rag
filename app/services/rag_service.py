"""Application service facade for ingestion, indexing, retrieval, and generation."""

from __future__ import annotations

import uuid
from typing import Any

from app.core.config import AppSettings
from app.generation.llm import build_llm_provider
from app.generation.pipeline import GenerationPipeline
from app.indexing.pipeline import IndexingPipeline
from app.ingestion.pipeline import IngestionPipeline
from app.retrieval.dense import DenseRetriever
from app.retrieval.mmr import MMRSelector
from app.retrieval.neighbor_expansion import NeighborExpander
from app.retrieval.pipeline import RetrievalPipeline
from app.retrieval.reranker import CrossEncoderReranker, LexicalReranker
from app.retrieval.sparse import SparseRetriever


class RagService:
    def __init__(self, settings: AppSettings | None = None) -> None:
        self.settings = settings or AppSettings.from_env()
        self.ingestion = IngestionPipeline(self.settings.ingestion)
        self.indexing = IndexingPipeline(self.settings)
        dense = DenseRetriever(self.indexing.embedding_provider, self.indexing.vector_store)
        sparse = SparseRetriever(self.indexing.sparse_index)
        mmr = MMRSelector(self.indexing.embedding_provider)
        neighbor = NeighborExpander(self.indexing.vector_store)
        reranker = self._build_reranker()
        self.retrieval = RetrievalPipeline(
            self.settings.retrieval,
            dense=dense,
            sparse=sparse,
            mmr=mmr,
            neighbor_expander=neighbor,
            reranker=reranker,
        )
        self.generation = GenerationPipeline(build_llm_provider(self.settings))

    def ingest(self, video_or_url: str, **metadata: Any) -> dict[str, Any]:
        result = self.ingestion.run(video_or_url, **metadata)
        documents = self.indexing.index_chunks(result.chunks)
        return {
            "video_id": result.metadata.video_id,
            "segments": len(result.cleaned_segments),
            "chunks": len(result.chunks),
            "indexed_documents": len(documents),
        }

    def query(self, question: str, video_id: str | None = None, tenant_id: str | None = None, user_id: str | None = None) -> dict[str, Any]:
        request_id = str(uuid.uuid4())
        filters = {"video_id": video_id, "tenant_id": tenant_id, "user_id": user_id}
        filters = {key: value for key, value in filters.items() if value is not None}
        documents, trace = self.retrieval.retrieve(question, filters=filters)
        trace_data = trace.model_dump() if hasattr(trace, "model_dump") else trace.dict()
        answer = self.generation.generate(question, documents, request_id, trace_data)
        return answer.model_dump() if hasattr(answer, "model_dump") else answer.dict()

    def list_videos(self) -> list[dict[str, Any]]:
        seen: dict[str, dict[str, Any]] = {}
        for document in self.indexing.vector_store.all_documents():
            video_id = document.metadata.get("video_id")
            if video_id and video_id not in seen:
                seen[video_id] = {
                    "video_id": video_id,
                    "title": document.metadata.get("title"),
                    "channel": document.metadata.get("channel"),
                    "language": document.metadata.get("language"),
                }
        return list(seen.values())

    def _build_reranker(self):
        if self.settings.environment == "test":
            return LexicalReranker()
        try:
            return CrossEncoderReranker(self.settings.reranker_model)
        except Exception:
            return LexicalReranker()
