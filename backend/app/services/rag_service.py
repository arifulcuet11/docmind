import os
from pathlib import Path
from typing import List

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_community.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain.schema import Document

from app.core.config import CHROMA_PERSIST_DIR, COLLECTION_NAME, CHUNK_SIZE, CHUNK_OVERLAP, RETRIEVER_TOP_K, UPLOAD_DIR
from app.core.llm_factory import get_llm, get_embeddings


class RAGService:
    def __init__(self):
        self.embeddings = get_embeddings()
        self.llm = get_llm()
        self.vectorstore = self._load_or_create_vectorstore()

    def _load_or_create_vectorstore(self) -> Chroma:
        return Chroma(
            collection_name=COLLECTION_NAME,
            embedding_function=self.embeddings,
            persist_directory=CHROMA_PERSIST_DIR,
        )

    def ingest_document(self, file_path: str) -> dict:
        """Load, chunk, and embed a document into the vector store."""
        path = Path(file_path)
        ext = path.suffix.lower()

        if ext == ".pdf":
            loader = PyPDFLoader(file_path)
        elif ext in (".txt", ".md"):
            loader = TextLoader(file_path)
        else:
            raise ValueError(f"Unsupported file type: {ext}")

        documents: List[Document] = loader.load()

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
        )
        chunks = splitter.split_documents(documents)

        self.vectorstore.add_documents(chunks)
        self.vectorstore.persist()

        return {
            "file": path.name,
            "chunks": len(chunks),
            "pages": len(documents),
        }

    def query(self, question: str) -> dict:
        """Answer a question using RAG over ingested documents."""
        qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            retriever=self.vectorstore.as_retriever(search_kwargs={"k": RETRIEVER_TOP_K}),
            return_source_documents=True,
        )
        result = qa_chain.invoke({"query": question})
        sources = list({doc.metadata.get("source", "unknown") for doc in result["source_documents"]})

        return {
            "answer": result["result"],
            "sources": sources,
        }

    def list_documents(self) -> List[str]:
        """Return a list of all ingested document sources."""
        collection = self.vectorstore._collection
        results = collection.get(include=["metadatas"])
        sources = list({m.get("source", "unknown") for m in results["metadatas"]})
        return sources

    def delete_document(self, filename: str) -> dict:
        """Delete all chunks of a document from vector store and disk."""
        # Build the full file path
        file_path = os.path.join(UPLOAD_DIR, filename)
 
        # Step 1 — find all chunk IDs in ChromaDB that belong to this file
        collection = self.vectorstore._collection
        results = collection.get(include=["metadatas"])
 
        ids_to_delete = [
            doc_id
            for doc_id, metadata in zip(results["ids"], results["metadatas"])
            if filename in metadata.get("source", "")
        ]
 
        if not ids_to_delete:
            raise FileNotFoundError(f"Document '{filename}' not found in vector store")
 
        # Step 2 — delete chunks from ChromaDB
        collection.delete(ids=ids_to_delete)
        self.vectorstore.persist()
 
        # Step 3 — delete file from disk
        if os.path.exists(file_path):
            os.remove(file_path)
 
        return {
            "file": filename,
            "message": f"Deleted '{filename}' and {len(ids_to_delete)} chunks from vector store",
        }
    
# Singleton instance
rag_service = RAGService()
