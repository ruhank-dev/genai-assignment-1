from typing import Any

from pydantic import BaseModel

from src.app.backend.schemas.common import Metrics


class UniversalRestoreResponse(BaseModel):
    original_image: str  # the uploaded image (clean sample when a corruption is applied)
    corrupted_image: str  # exactly what the model received
    restored_image: str
    error_map: str  # |restored - reference| heat map
    error_reference: str  # "clean_upload" (corruption applied here) | "input" (image uploaded as-is)
    corruption_applied: dict[str, Any] | None
    inference_time_ms: float
    metrics: Metrics  # restored vs reference
    input_metrics: Metrics | None  # corrupted input vs clean (only when the clean image is known)
