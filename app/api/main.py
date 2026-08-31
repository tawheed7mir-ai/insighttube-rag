"""FastAPI application factory."""

from fastapi import FastAPI

from app.api.routes.rag import router as rag_router


def create_app() -> FastAPI:
    app = FastAPI(title="YouTube Podcast RAG", version="0.1.0")
    app.include_router(rag_router)

    @app.get("/health")
    def health():
        return {"status": "ok"}

    @app.get("/ready")
    def ready():
        return {"status": "ready"}

    return app


app = create_app()
