from fastapi import APIRouter
from app.models.schemas import HealthResponse
from app.core.config import APP_NAME, APP_VERSION, LLM_PROVIDER, CURRENT_MODEL

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse)
async def health():
    return HealthResponse(
        status="ok",
        app=APP_NAME,
        version=APP_VERSION,
        provider=LLM_PROVIDER,
        model=CURRENT_MODEL,
    )
