"""RAG API routes."""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException

from app.api.dependencies import get_rag_service
from app.api.schemas import EvaluateRequest, IngestRequest, QueryRequest, TranscriptIngestRequest
from app.core.exceptions import TranscriptError, TranscriptUnavailableError
from app.services.rag_service import RagService

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/ingest")
def ingest(payload: IngestRequest, service: RagService = Depends(get_rag_service)):
    try:
        return service.ingest(
            payload.video_url,
            title=payload.title,
            channel=payload.channel,
            tenant_id=payload.tenant_id,
            user_id=payload.user_id,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except TranscriptUnavailableError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except TranscriptError as exc:
        logger.exception("Transcript ingestion failed")
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Unexpected ingestion failure")
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {exc}") from exc


@router.post("/ingest-transcript")
def ingest_transcript(payload: TranscriptIngestRequest, service: RagService = Depends(get_rag_service)):
    try:
        return service.ingest_transcript(
            payload.video_url,
            payload.transcript,
            title=payload.title,
            channel=payload.channel,
            tenant_id=payload.tenant_id,
            user_id=payload.user_id,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Transcript upload failed")
        raise HTTPException(status_code=500, detail=f"Transcript upload failed: {exc}") from exc


@router.post("/query")
def query(payload: QueryRequest, service: RagService = Depends(get_rag_service)):
    return service.query(payload.question, video_id=payload.video_id, tenant_id=payload.tenant_id, user_id=payload.user_id)


@router.get("/videos")
def videos(service: RagService = Depends(get_rag_service)):
    return service.list_videos()


@router.get("/videos/{video_id}")
def video(video_id: str, service: RagService = Depends(get_rag_service)):
    return [item for item in service.list_videos() if item["video_id"] == video_id]


@router.delete("/videos/{video_id}")
def delete_video(video_id: str):
    return {"status": "not_implemented", "message": "Delete hook exists; implement store-specific deletion before production use.", "video_id": video_id}


@router.post("/evaluate")
def evaluate(payload: EvaluateRequest):
    return {"status": "accepted", "dataset_path": payload.dataset_path}


@router.post("/rebuild-index")
def rebuild_index():
    return {"status": "not_implemented", "message": "Use scripts/rebuild_index.py for local rebuilds."}
