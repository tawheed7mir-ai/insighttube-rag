"""Metadata construction helpers."""

from __future__ import annotations

from app.ingestion.models import SourceMetadata


def build_source_metadata(
    *,
    video_id: str,
    language: str,
    source_type: str = "youtube",
    title: str | None = None,
    channel: str | None = None,
    tenant_id: str | None = None,
    user_id: str | None = None,
    version: str = "v1",
) -> SourceMetadata:
    source_url = f"https://www.youtube.com/watch?v={video_id}"
    return SourceMetadata(
        video_id=video_id,
        source_url=source_url,
        language=language,
        source_type=source_type,
        title=title,
        channel=channel,
        tenant_id=tenant_id,
        user_id=user_id,
        version=version,
    )

