# 🧠 DocMind — LLM Chatbot

A full-stack Document Q&A app powered by local LLMs (Ollama) or cloud APIs (OpenAI / Claude).  
Upload documents → Ask questions → Get intelligent answers with source references.

---

## Project Structure

```
docmind/
├── backend/      # Python · FastAPI · LangChain · ChromaDB
└── frontend/     # React · TypeScript · Tailwind CSS · Zustand
```

---

## Quick Start

### 1. Backend

```bash
cd backend

# Create & activate virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# LLM_PROVIDER=ollama by default — no changes needed for local dev

# Start Ollama (in a separate terminal)
ollama serve
ollama pull llama3.1:8b

# Run backend
uvicorn app.main:app --reload --port 8000
```

API docs: http://localhost:8000/docs

---

### 2. Frontend

```bash
cd frontend

# Install dependencies
npm install

# Configure environment
cp .env.example .env

# Run dev server
npm run dev
```

App: http://localhost:5173

---

## Switching LLM Provider

Edit `backend/.env`:

```bash
# Local (free, private)
LLM_PROVIDER=ollama

# OpenAI
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-...

# Anthropic Claude
LLM_PROVIDER=claude
ANTHROPIC_API_KEY=sk-ant-...
```

Restart the backend — frontend needs no changes.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python, FastAPI, LangChain |
| AI / LLM | Ollama (local), OpenAI, Claude |
| Vector DB | ChromaDB |
| Frontend | React 18, TypeScript, Vite |
| State | Zustand |
| Styling | Tailwind CSS |
| HTTP | Axios |

---

## Roadmap

- [ ] Streaming responses
- [ ] Multi-document session management
- [ ] Authentication
- [ ] Docker Compose setup
- [ ] Deploy to Azure
