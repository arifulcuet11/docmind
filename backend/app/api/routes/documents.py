import os
import shutil
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.models.schemas import DocumentIngested, DocumentListResponse, DocumentDeleted
from app.services.document_service import document_service
from app.core.config import UPLOAD_DIR

router = APIRouter(prefix="/documents", tags=["Documents"])

os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/upload", response_model=DocumentIngested)
async def upload_document(file: UploadFile = File(...)):
    """Upload and ingest a document (PDF, TXT, MD)."""
    file_path = os.path.join(UPLOAD_DIR, file.filename)

    # Save file to disk
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Validate file type and size
    size_mb = os.path.getsize(file_path) / (1024 * 1024)
    try:
        document_service.validate_file(file.filename, size_mb)
    except ValueError as e:
        os.remove(file_path)
        raise HTTPException(status_code=400, detail=str(e))

    # Ingest into vector store
    try:
        result = document_service.ingest(file_path)
        return DocumentIngested(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=DocumentListResponse)
async def list_documents():
    """List all ingested documents."""
    try:
        docs = document_service.list_documents()
        return DocumentListResponse(documents=docs, count=len(docs))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{filename}", response_model=DocumentDeleted)
async def delete_document(filename: str):
    """Delete a document from vector store and disk."""
    try:
        result = document_service.delete(filename)
        return DocumentDeleted(**result)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))