from pydantic import BaseModel

from src.app.backend.schemas.common import Metrics


class SoftMoERestoreResponse(BaseModel):
    original_image: str
    restored_image: str
    routing_weights: dict[str, float]  # identity_clean, expert_salt, expert_blur, expert_occlusion (sum to 1)
    dominant_expert: str
    inference_time_ms: float
    error_map: str
    error_reference: str  # "clean_reference" | "input"
    metrics: Metrics
    input_metrics: Metrics | None
