from app.core.config import AppSettings, IngestionSettings, RetrievalSettings
from app.ingestion.models import TranscriptSegment
from app.services.rag_service import RagService


class StubLoader:
    def fetch(self, video_or_url):
        return "Gfr50f6ZBvo", [
            TranscriptSegment(text="Nuclear fusion uses plasma in a tokamak.", start=0, duration=5, end=5),
            TranscriptSegment(text="AI can help control high temperature plasma.", start=5, duration=5, end=10),
        ]


def test_rag_service_ingest_query(tmp_path):
    settings = AppSettings(
        environment="test",
        data_dir=tmp_path,
        index_dir=tmp_path / "indexes",
        embedding_model="hash-embedding-v1",
        llm_provider="local",
        ingestion=IngestionSettings(chunk_size=120, chunk_overlap=0),
        retrieval=RetrievalSettings(rerank_top_k=2),
    )
    service = RagService(settings)
    service.ingestion.loader = StubLoader()
    ingested = service.ingest("https://www.youtube.com/watch?v=Gfr50f6ZBvo")
    assert ingested["chunks"] >= 1
    answer = service.query("What can AI help control?", video_id="Gfr50f6ZBvo")
    assert answer["request_id"]
    assert answer["citations"]
    assert "transcript" not in answer["answer"].lower() or answer["grounded"] is False
