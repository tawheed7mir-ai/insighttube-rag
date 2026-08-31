from app.services.rag_service import RagService

service = RagService()
video = input("YouTube URL or video ID: ").strip()
print(service.ingest(video))
