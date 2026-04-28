from typing import List, Optional
from langchain.schema import Document
from chromadb.errors import InvalidDimensionException

from app.core.llm_factory import get_llm
from app.services.vector_store_service import vector_store_service

HISTORY_BUFFER = 8  # keep last 8 messages (4 exchanges)

_PROMPT_TEMPLATE = """You are a helpful assistant. Use the context below to answer the question.
If the context contains relevant information, summarize and explain it clearly.
If the context does not contain enough information, say what you do know from it.

Context:
{context}
{history_section}
Question: {question}

Answer:"""

_DIMENSION_ERROR = (
    "Embedding dimension mismatch between stored collection and current embedding model. "
    "Either recreate the Chroma DB (delete ./chroma_db) and re-ingest documents, "
    "or use the same embedding model that was used to build the collection."
)


class RAGService:
    def __init__(self):
        self.llm = get_llm()

    def _retrieve(self, question: str, selected_sources: Optional[List[str]]) -> List[Document]:
        try:
            retriever = vector_store_service.search(query=question, sources=selected_sources)
            return retriever.get_relevant_documents(question)
        except InvalidDimensionException:
            raise ValueError(_DIMENSION_ERROR)

    def _build_prompt(self, question: str, docs: List[Document], chat_history: Optional[List[dict]]) -> str:
        context = "\n\n".join(doc.page_content for doc in docs)

        history_section = ""
        if chat_history:
            trimmed = chat_history[-HISTORY_BUFFER:]
            lines = ["Previous conversation:"]
            for msg in trimmed:
                role = "Human" if msg["role"] == "user" else "Assistant"
                lines.append(f"{role}: {msg['content']}")
            history_section = "\n" + "\n".join(lines) + "\n"

        return _PROMPT_TEMPLATE.format(
            context=context,
            history_section=history_section,
            question=question,
        )

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

    def query(self, question: str, selected_sources: Optional[List[str]] = None, chat_history: Optional[List[dict]] = None) -> dict:
        docs = self._retrieve(question, selected_sources)
        prompt_text = self._build_prompt(question, docs, chat_history)

        try:
            result = self.llm.invoke(prompt_text)
        except InvalidDimensionException:
            raise ValueError(_DIMENSION_ERROR)

        answer = self._extract_chunk_text(result)
        sources = list({doc.metadata.get("source", "unknown") for doc in docs})
        return {"answer": answer, "sources": sources}

    def stream(self, question: str, selected_sources: Optional[List[str]] = None, chat_history: Optional[List[dict]] = None):
        docs = self._retrieve(question, selected_sources)
        prompt_text = self._build_prompt(question, docs, chat_history)
        sources = list({doc.metadata.get("source", "unknown") for doc in docs})

        for chunk in self.llm.stream(prompt_text):
            text = self._extract_chunk_text(chunk)
            if text:
                yield {"type": "chunk", "text": text}

        yield {"type": "done", "sources": sources}


# Singleton
rag_service = RAGService()
