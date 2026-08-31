"""Transcript normalization."""

from __future__ import annotations

from app.ingestion.models import TranscriptSegment, update_model


class TranscriptNormalizer:
    """Apply deterministic text normalization after cleaning.

    The normalizer intentionally avoids aggressive transformations such as
    lowercasing, because names, acronyms, and technical terms matter for search.
    """

    def normalize_segments(
        self, segments: list[TranscriptSegment]
    ) -> list[TranscriptSegment]:
        normalized: list[TranscriptSegment] = []
        for segment in segments:
            text = segment.text.strip()
            normalized.append(update_model(segment, text=text))
        return normalized

