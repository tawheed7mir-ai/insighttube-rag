"""Indexing pipeline that updates dense and sparse indexes incrementally."""

from __future__ import annotations

from app.core.config import AppSettings
from app.domain import Document
from app.indexing.embeddings import EmbeddingProvider, HashEmbeddingProvider, SentenceTransformerEmbeddingProvider
from app.indexing.sparse_index import BM25Index
from app.indexing.vector_store import JsonVectorStore, build_documents_from_chunks


class IndexingPipeline:
    def __init__(
        self,
        settings: AppSettings,
        embedding_provider: EmbeddingProvider | None = None,
        vector_store: JsonVectorStore | None = None,
        sparse_index: BM25Index | None = None,
    ) -> None:
        self.settings = settings
        settings.index_dir.mkdir(parents=True, exist_ok=True)
        self.embedding_provider = embedding_provider or self._build_embedding_provider()
        self.vector_store = vector_store or JsonVectorStore(settings.index_dir / "vectors.json")
        self.sparse_index = sparse_index or BM25Index(settings.index_dir / "bm25.json")

    def index_chunks(self, chunks: list[object]) -> list[Document]:
        documents = build_documents_from_chunks(chunks)
        vectors = self.embedding_provider.embed_texts([document.text for document in documents])
        self.vector_store.upsert(documents, vectors)
        self.sparse_index.upsert(documents)
        return documents

    def _build_embedding_provider(self) -> EmbeddingProvider:
        if self.settings.environment == "test" or self.settings.embedding_model.startswith("hash"):
            return HashEmbeddingProvider(self.settings.embedding_model)
        try:
            return SentenceTransformerEmbeddingProvider(
                self.settings.embedding_model,
                batch_size=self.settings.embedding_batch_size,
            )
        except Exception:
            return HashEmbeddingProvider("hash-embedding-fallback")
