# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

DocMind is a full-stack Document Q&A (RAG) application. Users upload documents, which are chunked and stored in ChromaDB. Questions are answered by retrieving relevant chunks and passing them to an LLM. The backend is FastAPI + LangChain; the frontend is React 18 + TypeScript + Vite.

## Commands

### Backend

```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

API docs available at `http://localhost:8000/docs`.

### Frontend

```bash
cd frontend
npm run dev          # Dev server on port 5173
npm run build        # Production build
npm run lint         # ESLint
npm run type-check   # TypeScript without building
```

### No test suite exists yet — `backend/tests/` is empty.

## Architecture

### Backend (`backend/app/`)

The backend uses a service layer that routes cleanly own from FastAPI routes.

- **`core/config.py`** — Pydantic `Settings` loaded from `.env`. Single source of truth for all environment config.
- **`core/llm_factory.py`** — Factory that returns the correct LangChain LLM + embeddings based on `LLM_PROVIDER` env var. Supports `ollama`, `openai`, `claude`, `openrouter`. Switching providers is a one-line `.env` change.
- **`services/document_service.py`** — Loads files (PDF, TXT, MD, DOCX, CSV, XLSX), splits into chunks (`CHUNK_SIZE=500`, `CHUNK_OVERLAP=50`), and ingests into ChromaDB.
- **`services/vector_store_service.py`** — ChromaDB wrapper. Collections are namespaced by provider + embedding model so switching providers doesn't pollute existing collections. Contains `FilteredRetriever` for per-source document filtering.
- **`services/rag_service.py`** — Orchestrates retrieval + LLM invocation. Supports both blocking and SSE streaming responses.
- **`api/routes/`** — Thin route handlers that delegate to services. Three route files: `chat.py`, `documents.py`, `health.py`.

Services are module-level singletons — instantiated once at import time.

### Frontend (`frontend/src/`)

- **`store/index.ts`** — Central Zustand store (~850 lines). All chat and document state lives here. Chat sessions are persisted to `localStorage` under key `docmind_chat_sessions`. Streaming is handled in-store via the `ask()` action.
- **`services/api.ts`** — Axios client wrapping all backend calls. SSE streaming uses `fetch` directly (not Axios) in `streamMessage()`.
- **`types/index.ts`** — Shared TypeScript interfaces (`Message`, `ChatSession`, `Document`, etc.).
- **`App.tsx`** — Three-column layout: DocumentPanel (left), ChatWindow (center), ChatSessionsPanel (right, collapsible).

### RAG Data Flow

1. Upload → `document_service` loads + chunks → `vector_store_service` upserts into ChromaDB collection
2. Chat question → `rag_service` retrieves top-K chunks (filtered by selected sources if any) → builds prompt → calls LLM → streams or returns answer + source metadata

## Configuration

Copy `.env.example` to `.env` in `backend/`. Key variables:

```
LLM_PROVIDER=ollama          # ollama | openai | claude | openrouter
OLLAMA_BASE_URL=http://localhost:11434
CHUNK_SIZE=500
RETRIEVER_TOP_K=5
CORS_ORIGINS=http://localhost:5173
```

Frontend `.env` is minimal — just `VITE_API_URL` pointing to the backend.
