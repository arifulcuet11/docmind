from langchain_community.vectorstores import Chroma
from langchain.schema import Document
from typing import List

from app.core.config import CHROMA_PERSIST_DIR, COLLECTION_NAME, RETRIEVER_TOP_K
from app.core.llm_factory import get_embeddings


class VectorStoreService:
    """
    Responsible ONLY for ChromaDB vector store operations.
    - Add documents (chunks) to the store
    - Search for similar chunks
    - Delete chunks by source file
    - List all stored sources
    """

    def __init__(self):
        self.embeddings = get_embeddings()
        self.vectorstore = self._load_or_create()

    def _load_or_create(self) -> Chroma:
        """Load existing ChromaDB or create a new one."""
        return Chroma(
            collection_name=COLLECTION_NAME,
            embedding_function=self.embeddings,
            persist_directory=CHROMA_PERSIST_DIR,
        )

    def add_documents(self, chunks: List[Document]) -> None:
        """Add chunked documents to the vector store."""
        self.vectorstore.add_documents(chunks)
        self.vectorstore.persist()

    def search(self, query: str, top_k: int = RETRIEVER_TOP_K, sources: List[str] = None):
        """
        Search for similar chunks.
        Optionally filter by specific source files.
        """
        retriever_kwargs = {"k": top_k}

        # If specific sources selected, filter by them
        if sources:
            retriever_kwargs["filter"] = {"source": {"$in": sources}}

        return self.vectorstore.as_retriever(search_kwargs=retriever_kwargs)

    def delete_by_source(self, filename: str) -> int:
        """
        Delete all chunks belonging to a specific file.
        Returns number of chunks deleted.
        """
        collection = self.vectorstore._collection
        results = collection.get(include=["metadatas"])

        ids_to_delete = [
            doc_id
            for doc_id, metadata in zip(results["ids"], results["metadatas"])
            if filename in metadata.get("source", "")
        ]

        if not ids_to_delete:
            raise FileNotFoundError(f"Document '{filename}' not found in vector store")

        collection.delete(ids=ids_to_delete)
        self.vectorstore.persist()

        return len(ids_to_delete)

    def list_sources(self) -> List[str]:
        """Return all unique document sources stored in ChromaDB."""
        collection = self.vectorstore._collection
        results = collection.get(include=["metadatas"])
        sources = list({
            m.get("source", "unknown")
            for m in results["metadatas"]
        })
        return sources

    def get_vectorstore(self) -> Chroma:
        """Return the raw vectorstore (used by RAGService)."""
        return self.vectorstore


# Singleton
vector_store_service = VectorStoreService()