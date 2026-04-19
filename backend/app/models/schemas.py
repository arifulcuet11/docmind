from pydantic import BaseModel
from typing import List, Optional


class ChatRequest(BaseModel):
    question: str
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    answer: str
    sources: List[str] = []
    session_id: Optional[str] = None


class DocumentIngested(BaseModel):
    file: str
    chunks: int
    pages: int
    message: str = "Document ingested successfully"


class DocumentListResponse(BaseModel):
    documents: List[str]
    count: int

class DocumentDeleted(BaseModel):
    file: str
    message: str = "Document deleted successfully"
    
class HealthResponse(BaseModel):
    status: str
    app: str
    version: str
    provider: str
    model: str
