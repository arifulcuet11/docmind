import os
from pathlib import Path
from typing import List

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain.schema import Document

from app.core.config import UPLOAD_DIR, ALLOWED_EXTENSIONS, CHUNK_SIZE, CHUNK_OVERLAP
from app.services.vector_store_service import vector_store_service

os.makedirs(UPLOAD_DIR, exist_ok=True)


class DocumentService:
    """
    Responsible ONLY for document file operations.
    - Load files from disk
    - Split into chunks
    - Ingest into vector store
    - Delete from disk + vector store
    - List all documents
    """

    def ingest(self, file_path: str) -> dict:
        """
        Full ingestion pipeline:
        1. Load file from disk
        2. Split into chunks
        3. Store chunks in vector store
        """
        path = Path(file_path)
        ext = path.suffix.lower()

        # Step 1 — Load file
        loader = self._get_loader(file_path, ext)
        documents: List[Document] = loader.load()

        # Step 2 — Split into chunks
        chunks = self._split(documents)

        # Step 3 — Store in ChromaDB via VectorStoreService
        vector_store_service.add_documents(chunks)

        return {
            "file": path.name,
            "chunks": len(chunks),
            "pages": len(documents),
        }

    def delete(self, filename: str) -> dict:
        """
        Delete document from:
        1. ChromaDB vector store
        2. Disk (uploads folder)
        """
        # Step 1 — delete from vector store
        deleted_chunks = vector_store_service.delete_by_source(filename)

        # Step 2 — delete from disk
        file_path = os.path.join(UPLOAD_DIR, filename)
        if os.path.exists(file_path):
            os.remove(file_path)

        return {
            "file": filename,
            "message": f"Deleted '{filename}' and {deleted_chunks} chunks from vector store",
        }

    def list_documents(self) -> List[str]:
        """List all ingested document sources."""
        return vector_store_service.list_sources()

    def validate_file(self, filename: str, size_mb: float) -> None:
        """
        Validate file type and size.
        Raises ValueError if invalid.
        """
        ext = Path(filename).suffix.lower()

        if ext not in ALLOWED_EXTENSIONS:
            raise ValueError(f"File type '{ext}' not allowed. Supported: {ALLOWED_EXTENSIONS}")

        if size_mb > int(os.getenv("MAX_UPLOAD_SIZE_MB", "50")):
            raise ValueError(f"File too large. Max size: 50MB")

    # ── Private helpers ───────────────────────────────────────

    def _get_loader(self, file_path: str, ext: str):
        """Return the correct loader based on file extension."""
        if ext == ".pdf":
            return PyPDFLoader(file_path)
        elif ext in (".txt", ".md"):
            return TextLoader(file_path)
        else:
            raise ValueError(f"Unsupported file type: {ext}")

    def _split(self, documents: List[Document]) -> List[Document]:
        """Split documents into smaller chunks."""
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
        )
        return splitter.split_documents(documents)


# Singleton
document_service = DocumentService()