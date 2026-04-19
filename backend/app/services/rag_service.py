from typing import List, Optional
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

from app.core.llm_factory import get_llm
from app.services.vector_store_service import vector_store_service


class RAGService:
    """
    Responsible ONLY for answering questions using RAG.
    - Takes a question + optional source filter
    - Retrieves relevant chunks from VectorStoreService
    - Sends to LLM and returns answer
    """

    def __init__(self):
        self.llm = get_llm()

    def query(self, question: str, selected_sources: Optional[List[str]] = None) -> dict:
        """
        Answer a question using RAG.
        Optionally filter by selected_sources (list of file paths).
        """
        retriever = vector_store_service.search(
            query=question,
            sources=selected_sources,
        )

        prompt = PromptTemplate(
            input_variables=["context", "question"],
            template="""You are a helpful assistant. Use the context below to answer the question.
If the context contains relevant information, summarize and explain it clearly.
If the context does not contain enough information, say what you do know from it.

Context:
{context}

Question: {question}

Answer:"""
        )

        qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            retriever=retriever,
            return_source_documents=True,
            chain_type="stuff",
            chain_type_kwargs={"prompt": prompt},
        )

        result = qa_chain.invoke({"query": question})

        sources = list({
            doc.metadata.get("source", "unknown")
            for doc in result["source_documents"]
        })

        return {
            "answer": result["result"],
            "sources": sources,
        }


# Singleton
rag_service = RAGService()