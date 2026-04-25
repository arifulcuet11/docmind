from typing import List, Optional
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.schema import Document

from app.core.llm_factory import get_llm
from app.services.vector_store_service import vector_store_service
from chromadb.errors import InvalidDimensionException


class RAGService:
    """
    Responsible ONLY for answering questions using RAG.
    - Takes a question + optional source filter
    - Retrieves relevant chunks from VectorStoreService
    - Sends to LLM and returns answer
    """

    def __init__(self):
        self.llm = get_llm()
        self.prompt = PromptTemplate(
            input_variables=["context", "question"],
            template="""You are a helpful assistant. Use the context below to answer the question.
If the context contains relevant information, summarize and explain it clearly.
If the context does not contain enough information, say what you do know from it.

Context:
{context}

Question: {question}

Answer:"""
        )

    def _build_prompt(self, question: str, docs: List[Document]) -> str:
        context = "\n\n".join(doc.page_content for doc in docs)
        return self.prompt.format(context=context, question=question)

    def _extract_chunk_text(self, chunk: any) -> str:
        if isinstance(chunk, str):
            return chunk

        if chunk is None:
            return ""

        if hasattr(chunk, "content"):
            content = chunk.content
            if isinstance(content, str):
                return content
            if isinstance(content, dict):
                return content.get("content", "") or content.get("text", "")

        if hasattr(chunk, "text"):
            text = chunk.text
            if isinstance(text, str):
                return text

        if isinstance(chunk, dict):
            return chunk.get("content", "") or chunk.get("text", "") or ""

        return str(chunk)

    def query(self, question: str, selected_sources: Optional[List[str]] = None) -> dict:
        """
        Answer a question using RAG.
        Optionally filter by selected_sources (list of file paths).
        """
        try:
            retriever = vector_store_service.search(
                query=question,
                sources=selected_sources,
            )
        except InvalidDimensionException as e:
            raise ValueError(
                "Embedding dimension mismatch between stored collection and current embedding model. "
                "Either recreate the Chroma DB (delete ./chroma_db) and re-ingest documents, or use the same embedding model that was used to build the collection."
            )

        qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            retriever=retriever,
            return_source_documents=True,
            chain_type="stuff",
            chain_type_kwargs={"prompt": self.prompt},
        )

        # Execute the chain. Wrap invocation to catch Chroma dimension errors
        try:
            result = qa_chain({"query": question})
        except InvalidDimensionException:
            raise ValueError(
                "Embedding dimension mismatch between stored collection and current embedding model. "
                "Either recreate the Chroma DB (delete ./chroma_db) and re-ingest documents, or use the same embedding model that was used to build the collection."
            )

        # Normalize result shape for compatibility across versions
        if isinstance(result, str):
            answer = result
            source_docs = []
        elif isinstance(result, dict):
            answer = result.get("result") or result.get("output") or ""
            source_docs = result.get("source_documents") or []
        else:
            answer = str(result)
            source_docs = []

        sources = list({
            getattr(doc, "metadata", {}).get("source", "unknown")
            for doc in source_docs
        })

        return {
            "answer": answer,
            "sources": sources,
        }

    def stream(self, question: str, selected_sources: Optional[List[str]] = None):
        retriever = vector_store_service.search(
            query=question,
            sources=selected_sources,
        )
        docs = retriever.get_relevant_documents(question)
        prompt_text = self._build_prompt(question, docs)

        sources = list({
            doc.metadata.get("source", "unknown")
            for doc in docs
        })

        for chunk in self.llm.stream(prompt_text):
            text = self._extract_chunk_text(chunk)
            if text:
                yield {"type": "chunk", "text": text}

        yield {"type": "done", "sources": sources}


# Singleton
rag_service = RAGService()