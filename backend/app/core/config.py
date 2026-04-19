import os
from dotenv import load_dotenv

load_dotenv()

# ── LLM Provider ─────────────────────────────────────────────
# Options: "ollama" | "openai" | "claude"
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama")

# ── Model names per provider ──────────────────────────────────
MODELS = {
    "ollama": os.getenv("OLLAMA_MODEL", "llama3.1:8b"),
    "openai": os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
    "claude": os.getenv("CLAUDE_MODEL", "claude-sonnet-4-20250514"),
}

CURRENT_MODEL = MODELS[LLM_PROVIDER]

# ── API Keys ──────────────────────────────────────────────────
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

# ── Ollama ────────────────────────────────────────────────────
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

# ── Vector Store ──────────────────────────────────────────────
CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "docmind")

# ── Document Upload ───────────────────────────────────────────
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "./uploads")
MAX_UPLOAD_SIZE_MB = int(os.getenv("MAX_UPLOAD_SIZE_MB", "50"))
ALLOWED_EXTENSIONS = {".pdf", ".txt", ".md", ".docx"}

# ── RAG Settings ──────────────────────────────────────────────
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "500"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "50"))
RETRIEVER_TOP_K = int(os.getenv("RETRIEVER_TOP_K", "5"))

# ── App ───────────────────────────────────────────────────────
APP_NAME = "DocMind"
APP_VERSION = "0.1.0"
DEBUG = os.getenv("DEBUG", "true").lower() == "true"
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
