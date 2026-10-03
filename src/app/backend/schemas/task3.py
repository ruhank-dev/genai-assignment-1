from pydantic import BaseModel


class SoftMoERestoreResponse(BaseModel):
    original_image: str
    restored_image: str
    routing_weights: dict[str, float]  # identity_clean, expert_salt, expert_blur, expert_occlusion (sum to 1)
    dominant_expert: str
    inference_time_ms: float
