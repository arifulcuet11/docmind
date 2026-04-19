import os
import shutil
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.models.schemas import DocumentIngested, DocumentListResponse
from app.services.rag_service import rag_service
from app.core.config import UPLOAD_DIR, ALLOWED_EXTENSIONS, MAX_UPLOAD_SIZE_MB

router = APIRouter(prefix="/documents", tags=["Documents"])

os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/upload", response_model=DocumentIngested)
async def upload_document(file: UploadFile = File(...)):
    """Upload and ingest a document (PDF, TXT, MD)."""
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"File type not allowed. Supported: {ALLOWED_EXTENSIONS}")

    file_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Check file size
    size_mb = os.path.getsize(file_path) / (1024 * 1024)
    if size_mb > MAX_UPLOAD_SIZE_MB:
        os.remove(file_path)
        raise HTTPException(status_code=400, detail=f"File too large. Max size: {MAX_UPLOAD_SIZE_MB}MB")

    try:
        result = rag_service.ingest_document(file_path)
        return DocumentIngested(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=DocumentListResponse)
async def list_documents():
    """List all ingested documents."""
    try:
        docs = rag_service.list_documents()
        return DocumentListResponse(documents=docs, count=len(docs))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
