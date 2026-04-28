from pydantic import BaseModel
from typing import List, Optional


class ChatHistoryMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str


class ChatRequest(BaseModel):
    question: str
    session_id: Optional[str] = None
    selected_sources: Optional[List[str]] = None  # filter by these docs
    chat_history: Optional[List[ChatHistoryMessage]] = None


class ChatResponse(BaseModel):
    answer: str
    sources: List[str] = []
    session_id: Optional[str] = None


class DocumentIngested(BaseModel):
    file: str
    chunks: int
    pages: int
    message: str = "Document ingested successfully"


class DocumentDeleted(BaseModel):
    file: str
    message: str = "Document deleted successfully"


class DocumentListResponse(BaseModel):
    documents: List[str]
    count: int


class HealthResponse(BaseModel):
    status: str
    app: str
    version: str
    provider: str
    model: str