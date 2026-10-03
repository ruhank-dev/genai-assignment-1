from fastapi import APIRouter, Request

from src.app.backend.schemas.common import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def health(request: Request) -> HealthResponse:
    reg = request.app.state.registry
    loaded = reg.loaded()
    return HealthResponse(status="ok" if all(loaded.values()) else "degraded", models_loaded=loaded,
                          providers=reg.providers)
