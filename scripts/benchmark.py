import time
from app.services.rag_service import RagService

service = RagService()
start = time.perf_counter()
print(service.query("What is this transcript about?"))
print({"latency_ms": round((time.perf_counter() - start) * 1000, 3)})
