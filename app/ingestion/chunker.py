"""Timestamp-aware transcript chunking."""

from __future__ import annotations

from app.ingestion.models import (
    SourceMetadata,
    TranscriptChunk,
    TranscriptSegment,
    format_timestamp,
    stable_hash,
    update_model,
)


class TimestampAwareChunker:
    """Chunk transcripts on segment boundaries while preserving evidence spans."""

    def __init__(self, chunk_size: int = 1500, chunk_overlap: int = 300) -> None:
        if chunk_size <= 0:
            raise ValueError("chunk_size must be positive")
        if chunk_overlap < 0:
            raise ValueError("chunk_overlap cannot be negative")
        if chunk_overlap >= chunk_size:
            raise ValueError("chunk_overlap must be smaller than chunk_size")
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk(
        self,
        segments: list[TranscriptSegment],
        metadata: SourceMetadata,
    ) -> list[TranscriptChunk]:
        chunks: list[TranscriptChunk] = []
        current: list[TranscriptSegment] = []
        current_chars = 0

        for segment in segments:
            segment_len = len(segment.text) + 1
            should_flush = current and current_chars + segment_len > self.chunk_size
            if should_flush:
                chunks.append(self._build_chunk(current, metadata, len(chunks)))
                current = self._overlap_tail(current)
                current_chars = sum(len(item.text) + 1 for item in current)

            current.append(segment)
            current_chars += segment_len

        if current:
            chunks.append(self._build_chunk(current, metadata, len(chunks)))

        for index, chunk in enumerate(chunks):
            previous_id = chunks[index - 1].chunk_id if index > 0 else None
            next_id = chunks[index + 1].chunk_id if index < len(chunks) - 1 else None
            chunks[index] = update_model(
                chunk,
                previous_chunk_id=previous_id,
                next_chunk_id=next_id,
            )

        return chunks

    def _overlap_tail(
        self, segments: list[TranscriptSegment]
    ) -> list[TranscriptSegment]:
        if self.chunk_overlap == 0:
            return []

        tail: list[TranscriptSegment] = []
        total_chars = 0
        for segment in reversed(segments):
            projected = total_chars + len(segment.text) + 1
            if tail and projected > self.chunk_overlap:
                break
            tail.insert(0, segment)
            total_chars = projected
        return tail

    def _build_chunk(
        self,
        segments: list[TranscriptSegment],
        metadata: SourceMetadata,
        chunk_number: int,
    ) -> TranscriptChunk:
        text = " ".join(segment.text for segment in segments).strip()
        start_time = segments[0].start
        end_time = max(segment.end for segment in segments)
        content_hash = stable_hash(
            f"{metadata.video_id}:{start_time:.3f}:{end_time:.3f}:{text}",
            length=24,
        )
        chunk_id = stable_hash(
            f"{metadata.video_id}:{chunk_number}:{content_hash}",
            length=24,
        )

        return TranscriptChunk(
            text=text,
            video_id=metadata.video_id,
            source_url=f"{metadata.source_url}&t={int(start_time)}s",
            chunk_id=chunk_id,
            chunk_number=chunk_number,
            start_time=start_time,
            end_time=end_time,
            start_timestamp=format_timestamp(start_time),
            end_timestamp=format_timestamp(end_time),
            language=metadata.language,
            source_type=metadata.source_type,
            content_hash=content_hash,
            version=metadata.version,
            title=metadata.title,
            channel=metadata.channel,
            speaker=metadata.speaker,
            tenant_id=metadata.tenant_id,
            user_id=metadata.user_id,
            segment_count=len(segments),
        )

