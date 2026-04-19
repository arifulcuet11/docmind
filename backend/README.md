# DocMind — Backend

FastAPI + LangChain + ChromaDB powered RAG backend.  
Swap between **Ollama (local)**, **OpenAI**, or **Claude** with one env variable.

## Quick Start

```bash
cd backend

# 1. Create virtual environment
python -m venv venv
source venv/bin/activate      # Mac/Linux
# venv\Scripts\activate       # Windows

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env — set LLM_PROVIDER=ollama (default)

# 4. Make sure Ollama is running
ollama serve
ollama pull llama3.1:8b

# 5. Run the server
uvicorn app.main:app --reload --port 8000
```

API docs available at: http://localhost:8000/docs

## Switching LLM Provider

Edit `.env`:
```
LLM_PROVIDER=ollama    # local development (free)
LLM_PROVIDER=openai    # OpenAI GPT
LLM_PROVIDER=claude    # Anthropic Claude
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /health | Health check + current provider info |
| POST | /api/v1/documents/upload | Upload & ingest a document |
| GET | /api/v1/documents/ | List all ingested documents |
| POST | /api/v1/chat/ | Ask a question |

## Project Structure

```
backend/
├── app/
│   ├── api/routes/
│   │   ├── chat.py          # POST /chat
│   │   ├── documents.py     # Upload & list docs
│   │   └── health.py        # Health check
│   ├── core/
│   │   ├── config.py        # All settings from .env
│   │   └── llm_factory.py   # Swap LLM providers here
│   ├── models/
│   │   └── schemas.py       # Pydantic request/response models
│   ├── services/
│   │   └── rag_service.py   # RAG logic (ingest + query)
│   └── main.py              # FastAPI app entry point
├── tests/
├── uploads/                 # Uploaded documents stored here
├── requirements.txt
└── .env.example
```
