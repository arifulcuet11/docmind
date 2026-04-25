import os
from langchain_community.vectorstores import Chroma
from langchain.schema import BaseRetriever, Document
from typing import List

from app.core.config import CHROMA_PERSIST_DIR, COLLECTION_NAME, RETRIEVER_TOP_K
from app.core.llm_factory import get_embeddings
from app.core.config import LLM_PROVIDER, CURRENT_EMBEDDING_MODEL


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
        # Namespace collections and persistence by provider + embedding model
        embed_model_safe = (CURRENT_EMBEDDING_MODEL or "default").replace("/", "_").replace(":", "_")
        namespaced_collection = f"{COLLECTION_NAME}_{LLM_PROVIDER}_{embed_model_safe}"
        persist_dir = os.path.join(CHROMA_PERSIST_DIR, namespaced_collection)
        os.makedirs(persist_dir, exist_ok=True)

        return Chroma(
            collection_name=namespaced_collection,
            embedding_function=self.embeddings,
            persist_directory=persist_dir,
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
        if sources:
            # For ChromaDB filtering, we need to use a different approach
            # Retrieve documents separately for each source to ensure fair distribution
            class FilteredRetriever(BaseRetriever):
                allowed_sources: List[str]
                max_results: int
                vectorstore: any

                def __init__(self, **kwargs):
                    super().__init__(**kwargs)

                def get_relevant_documents(self, query: str) -> List[Document]:
                    # Get a large number of documents to ensure we have docs from all sources
                    base_retriever = self.vectorstore.as_retriever(search_kwargs={"k": 100})
                    all_docs = base_retriever.get_relevant_documents(query)
                    
                    # Filter by allowed sources
                    filtered_docs = [
                        doc for doc in all_docs 
                        if doc.metadata.get("source") in self.allowed_sources
                    ]
                    
                    # Group by source and take top docs from each
                    docs_by_source = {}
                    for doc in filtered_docs:
                        source = doc.metadata.get("source")
                        if source not in docs_by_source:
                            docs_by_source[source] = []
                        docs_by_source[source].append(doc)
                    
                    # Take top documents from each source
                    result_docs = []
                    docs_per_source = max(1, self.max_results // len(self.allowed_sources))
                    
                    for source_docs in docs_by_source.values():
                        # Sort by relevance (assuming they're already sorted by the retriever)
                        result_docs.extend(source_docs[:docs_per_source])
                    
                    return result_docs[:self.max_results]

                async def aget_relevant_documents(self, query: str) -> List[Document]:
                    # For async support
                    docs = await self.base_retriever.aget_relevant_documents(query)
                    # Group documents by source
                    docs_by_source = {}
                    for doc in docs:
                        source = doc.metadata.get("source")
                        if source in self.allowed_sources:
                            if source not in docs_by_source:
                                docs_by_source[source] = []
                            docs_by_source[source].append(doc)
                    
                    # Take top documents from each source
                    result_docs = []
                    docs_per_source = max(1, self.max_results // len(self.allowed_sources))
                    
                    for source_docs in docs_by_source.values():
                        result_docs.extend(source_docs[:docs_per_source])
                    
                    # If we don't have enough docs, fill with remaining docs
                    if len(result_docs) < self.max_results:
                        for source_docs in docs_by_source.values():
                            for doc in source_docs[docs_per_source:]:
                                if len(result_docs) >= self.max_results:
                                    break
                                result_docs.append(doc)
                    
                    return result_docs[:self.max_results]

            return FilteredRetriever(
                vectorstore=self.vectorstore, 
                allowed_sources=sources, 
                max_results=top_k
            )
        else:
            # No filtering needed
            return self.vectorstore.as_retriever(search_kwargs={"k": top_k})

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