"""YouTube transcript loading.

The loader returns raw timestamped segments instead of flattened text so later
pipeline stages can build trustworthy citations and timestamp links.
"""

from __future__ import annotations

import logging
import re
from urllib.parse import parse_qs, urlparse

from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    NoTranscriptFound,
    TranscriptsDisabled,
    VideoUnavailable,
)

from app.core.exceptions import TranscriptError, TranscriptUnavailableError
from app.ingestion.models import TranscriptSegment

logger = logging.getLogger(__name__)

YOUTUBE_ID_RE = re.compile(r"^[A-Za-z0-9_-]{11}$")


def extract_video_id(value: str) -> str:
    candidate = value.strip()
    if YOUTUBE_ID_RE.match(candidate):
        return candidate

    parsed = urlparse(candidate)
    host = parsed.netloc.lower()
    if host.endswith("youtu.be"):
        video_id = parsed.path.strip("/").split("/")[0]
    elif "youtube.com" in host:
        if parsed.path == "/watch":
            video_id = parse_qs(parsed.query).get("v", [""])[0]
        elif parsed.path.startswith("/shorts/") or parsed.path.startswith("/embed/"):
            video_id = parsed.path.strip("/").split("/")[1]
        else:
            video_id = ""
    else:
        video_id = ""

    if not YOUTUBE_ID_RE.match(video_id):
        raise ValueError(f"Invalid YouTube video id or URL: {value}")
    return video_id


class YouTubeTranscriptLoader:
    def __init__(self, language: str = "en") -> None:
        self.language = language

    def fetch(self, video_or_url: str) -> tuple[str, list[TranscriptSegment]]:
        video_id = extract_video_id(video_or_url)
        logger.info("Fetching transcript", extra={"video_id": video_id})

        try:
            api = YouTubeTranscriptApi()
            fetched = api.fetch(video_id, languages=[self.language])
        except (TranscriptsDisabled, NoTranscriptFound, VideoUnavailable) as exc:
            raise TranscriptUnavailableError(
                f"Transcript is unavailable for video {video_id}"
            ) from exc
        except Exception as exc:
            logger.exception("YouTube transcript provider failed", extra={"video_id": video_id})
            raise TranscriptError(
                f"YouTube could not provide a transcript for video {video_id}: {exc}"
            ) from exc

        segments = [TranscriptSegment.from_api_snippet(snippet) for snippet in fetched]
        if not segments:
            raise TranscriptUnavailableError(
                f"Transcript returned no segments for video {video_id}"
            )
        return video_id, segments

    