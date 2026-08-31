"""Transcript cleaning utilities."""

from __future__ import annotations

import html
import re

from app.ingestion.models import TranscriptSegment, update_model

BRACKET_NOISE_RE = re.compile(r"\[(music|applause|laughter|noise|silence)\]", re.I)
WHITESPACE_RE = re.compile(r"\s+")


class TranscriptCleaner:
    """Remove obvious caption artifacts without destroying meaningful speech."""

    def clean_text(self, text: str) -> str:
        cleaned = html.unescape(text)
        cleaned = re.sub(r"<[^>]+>", " ", cleaned)
        cleaned = BRACKET_NOISE_RE.sub(" ", cleaned)
        cleaned = cleaned.replace("\ufeff", " ")
        cleaned = WHITESPACE_RE.sub(" ", cleaned).strip()
        return cleaned

    def clean_segments(
        self, segments: list[TranscriptSegment]
    ) -> list[TranscriptSegment]:
        cleaned_segments: list[TranscriptSegment] = []
        for segment in segments:
            text = self.clean_text(segment.text)
            if text:
                cleaned_segments.append(update_model(segment, text=text))
        return cleaned_segments

