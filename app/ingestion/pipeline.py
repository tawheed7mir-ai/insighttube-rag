"""Phase 1 ingestion pipeline orchestration."""

from __future__ import annotations

from app.core.config import IngestionSettings
from app.ingestion.chunker import TimestampAwareChunker
from app.ingestion.cleaner import TranscriptCleaner
from app.ingestion.metadata import build_source_metadata
from app.ingestion.models import IngestionResult, TranscriptSegment
from app.ingestion.normalizer import TranscriptNormalizer
from app.ingestion.youtube import YouTubeTranscriptLoader


class IngestionPipeline:
    """Coordinate transcript loading, cleaning, normalization, and chunking."""

    def __init__(
        self,
        settings: IngestionSettings | None = None,
        loader: YouTubeTranscriptLoader | None = None,
        cleaner: TranscriptCleaner | None = None,
        normalizer: TranscriptNormalizer | None = None,
        chunker: TimestampAwareChunker | None = None,
    ) -> None:
        self.settings = settings or IngestionSettings.from_env()
        self.loader = loader or YouTubeTranscriptLoader(self.settings.youtube_language)
        self.cleaner = cleaner or TranscriptCleaner()
        self.normalizer = normalizer or TranscriptNormalizer()
        self.chunker = chunker or TimestampAwareChunker(
            chunk_size=self.settings.chunk_size,
            chunk_overlap=self.settings.chunk_overlap,
        )

    def run(
        self,
        video_or_url: str,
        *,
        title: str | None = None,
        channel: str | None = None,
        tenant_id: str | None = None,
        user_id: str | None = None,
    ) -> IngestionResult:
        video_id, raw_segments = self.loader.fetch(video_or_url)
        return self.run_segments(
            video_id=video_id,
            raw_segments=raw_segments,
            title=title,
            channel=channel,
            tenant_id=tenant_id,
            user_id=user_id,
        )

    def run_segments(
        self,
        *,
        video_id: str,
        raw_segments: list[TranscriptSegment],
        title: str | None = None,
        channel: str | None = None,
        tenant_id: str | None = None,
        user_id: str | None = None,
    ) -> IngestionResult:
        metadata = build_source_metadata(
            video_id=video_id,
            language=self.settings.youtube_language,
            source_type=self.settings.source_type,
            title=title,
            channel=channel,
            tenant_id=tenant_id,
            user_id=user_id,
            version=self.settings.metadata_version,
        )
        cleaned = self.cleaner.clean_segments(raw_segments)
        normalized = self.normalizer.normalize_segments(cleaned)
        chunks = self.chunker.chunk(normalized, metadata)
        return IngestionResult(
            metadata=metadata,
            raw_segments=raw_segments,
            cleaned_segments=normalized,
            chunks=chunks,
        )

