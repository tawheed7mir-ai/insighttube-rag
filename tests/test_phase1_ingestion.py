from app.core.config import IngestionSettings
from app.ingestion.chunker import TimestampAwareChunker
from app.ingestion.cleaner import TranscriptCleaner
from app.ingestion.models import TranscriptSegment, format_timestamp
from app.ingestion.pipeline import IngestionPipeline
from app.ingestion.youtube import extract_video_id


def make_segments():
    return [
        TranscriptSegment(text="First useful sentence.", start=0.0, duration=4.0, end=4.0),
        TranscriptSegment(text="Second sentence has evidence.", start=4.0, duration=5.5, end=9.5),
        TranscriptSegment(text="Third sentence continues the idea.", start=9.5, duration=6.0, end=15.5),
        TranscriptSegment(text="Fourth sentence starts another detail.", start=15.5, duration=4.5, end=20.0),
    ]


def test_extract_video_id_from_common_youtube_urls():
    assert extract_video_id("Gfr50f6ZBvo") == "Gfr50f6ZBvo"
    assert extract_video_id("https://youtu.be/Gfr50f6ZBvo?t=1") == "Gfr50f6ZBvo"
    assert extract_video_id("https://www.youtube.com/watch?v=Gfr50f6ZBvo") == "Gfr50f6ZBvo"
    assert extract_video_id("https://www.youtube.com/shorts/Gfr50f6ZBvo") == "Gfr50f6ZBvo"


def test_timestamp_formatting_uses_video_style_timecodes():
    assert format_timestamp(62.8) == "01:02"
    assert format_timestamp(3721.2) == "01:02:01"


def test_cleaner_removes_caption_artifacts_but_keeps_speech():
    cleaner = TranscriptCleaner()
    cleaned = cleaner.clean_text("  Hello&nbsp;there <i>friend</i> [Music]  ")
    assert cleaned == "Hello there friend"


def test_pipeline_preserves_timestamps_metadata_and_deterministic_ids():
    settings = IngestionSettings(
        youtube_language="en",
        chunk_size=75,
        chunk_overlap=25,
        metadata_version="test-v1",
    )
    pipeline = IngestionPipeline(
        settings=settings,
        loader=None,
        chunker=TimestampAwareChunker(chunk_size=75, chunk_overlap=25),
    )

    first = pipeline.run_segments(
        video_id="Gfr50f6ZBvo",
        raw_segments=make_segments(),
        title="Demo",
        channel="Test Channel",
        tenant_id="tenant-a",
        user_id="user-a",
    )
    second = pipeline.run_segments(
        video_id="Gfr50f6ZBvo",
        raw_segments=make_segments(),
        title="Demo",
        channel="Test Channel",
        tenant_id="tenant-a",
        user_id="user-a",
    )

    assert len(first.raw_segments) == 4
    assert len(first.chunks) >= 2
    assert [chunk.chunk_id for chunk in first.chunks] == [
        chunk.chunk_id for chunk in second.chunks
    ]

    first_chunk = first.chunks[0]
    assert first_chunk.video_id == "Gfr50f6ZBvo"
    assert first_chunk.title == "Demo"
    assert first_chunk.channel == "Test Channel"
    assert first_chunk.tenant_id == "tenant-a"
    assert first_chunk.user_id == "user-a"
    assert first_chunk.start_time == 0.0
    assert first_chunk.start_timestamp == "00:00"
    assert first_chunk.source_url.endswith("&t=0s")
    assert first_chunk.next_chunk_id == first.chunks[1].chunk_id
    assert first.chunks[1].previous_chunk_id == first_chunk.chunk_id


def test_chunk_ranges_cover_segment_boundaries():
    settings = IngestionSettings(chunk_size=65, chunk_overlap=0)
    pipeline = IngestionPipeline(settings=settings)
    result = pipeline.run_segments(video_id="Gfr50f6ZBvo", raw_segments=make_segments())

    assert result.chunks[0].start_time == 0.0
    assert result.chunks[0].end_time >= 9.5
    assert result.chunks[-1].end_time == 20.0
    assert all(chunk.segment_count >= 1 for chunk in result.chunks)

