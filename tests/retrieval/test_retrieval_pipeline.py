from app.core.config import AppSettings, IngestionSettings, RetrievalSettings
from app.indexing.embeddings import HashEmbeddingProvider
from app.indexing.pipeline import IndexingPipeline
from app.ingestion.models import TranscriptSegment
from app.ingestion.pipeline import IngestionPipeline
from app.retrieval.dense import DenseRetriever
from app.retrieval.mmr import MMRSelector
from app.retrieval.neighbor_expansion import NeighborExpander
from app.retrieval.pipeline import RetrievalPipeline
from app.retrieval.sparse import SparseRetriever


def _segments():
    return [
        TranscriptSegment(text="Babar Azam is a Pakistani cricketer.", start=0, duration=4, end=4),
        TranscriptSegment(text="He is known for his batting.", start=4, duration=4, end=8),
        TranscriptSegment(text="Sachin Tendulkar represented India internationally.", start=8, duration=4, end=12),
    ]


def test_indexing_and_hybrid_retrieval(tmp_path):
    settings = AppSettings(
        environment="test",
        data_dir=tmp_path,
        index_dir=tmp_path / "indexes",
        embedding_model="hash-embedding-v1",
        ingestion=IngestionSettings(chunk_size=80, chunk_overlap=0),
        retrieval=RetrievalSettings(top_k=3, rerank_top_k=2),
    )
    ingestion = IngestionPipeline(settings.ingestion)
    result = ingestion.run_segments(video_id="Gfr50f6ZBvo", raw_segments=_segments())
    indexing = IndexingPipeline(settings, embedding_provider=HashEmbeddingProvider())
    indexing.index_chunks(result.chunks)

    pipeline = RetrievalPipeline(
        settings.retrieval,
        DenseRetriever(indexing.embedding_provider, indexing.vector_store),
        SparseRetriever(indexing.sparse_index),
        MMRSelector(indexing.embedding_provider),
        NeighborExpander(indexing.vector_store),
    )
    docs, trace = pipeline.retrieve("Who is Babar Azam?", filters={"video_id": "Gfr50f6ZBvo"})
    assert docs
    assert any("Babar" in item.document.text for item in docs)
    assert trace.final_chunk_ids
