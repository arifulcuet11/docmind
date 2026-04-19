from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import APP_NAME, APP_VERSION, DEBUG, CORS_ORIGINS
from app.api.routes import chat, documents, health

app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    description="LLM-powered Document Q&A — local (Ollama) or cloud (OpenAI/Claude)",
    debug=DEBUG,
)

# ── CORS ──────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routes ────────────────────────────────────────────────────
app.include_router(health.router)
app.include_router(chat.router,      prefix="/api/v1")
app.include_router(documents.router, prefix="/api/v1")


@app.get("/")
async def root():
    return {"message": f"Welcome to {APP_NAME} API", "docs": "/docs"}
