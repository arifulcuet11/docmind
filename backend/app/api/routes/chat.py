from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
import json

from app.models.schemas import ChatRequest, ChatResponse
from app.services.rag_service import rag_service

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Ask a question — answered using RAG over selected documents."""
    try:
        result = rag_service.query(
            question=request.question,
            selected_sources=request.selected_sources or None,
        )
        return ChatResponse(
            answer=result["answer"],
            sources=result["sources"],
            session_id=request.session_id,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stream")
def stream_chat(request: ChatRequest):
    """Stream the chat response back to the client token by token."""

    def event_generator():
        try:
            for event in rag_service.stream(
                question=request.question,
                selected_sources=request.selected_sources or None,
            ):
                if event.get("type") == "done":
                    event["session_id"] = request.session_id
                yield f"data: {json.dumps(event)}\n\n"
        except Exception as e:
            error_event = {"type": "error", "error": str(e)}
            yield f"data: {json.dumps(error_event)}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")