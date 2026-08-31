# Ingestion

Ingestion accepts a YouTube URL or video ID, extracts the video ID, fetches timestamped transcript segments, cleans obvious subtitle artifacts, normalizes text conservatively, and creates metadata-rich chunks. Chunks preserve start/end timestamps and previous/next relationships for citations and neighbor expansion.
