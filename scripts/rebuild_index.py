from app.services.rag_service import RagService

service = RagService()
print("Current local index is persistent under configured INDEX_DIR.")
print({"videos": service.list_videos()})
