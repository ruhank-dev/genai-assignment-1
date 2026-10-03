from pydantic import BaseModel


class ErrorResponse(BaseModel):
    detail: str


class HealthResponse(BaseModel):
    status: str
    models_loaded: dict[str, bool]
    providers: list[str]
