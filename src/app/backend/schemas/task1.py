from typing import Any

from pydantic import BaseModel


class UniversalRestoreResponse(BaseModel):
    original_image: str  # the uploaded image (clean sample when a corruption is applied)
    corrupted_image: str  # exactly what the model received
    restored_image: str
    error_map: str  # |restored - reference|, reference = clean upload if corruption was applied else the input
    error_reference: str  # "clean_upload" | "input"
    corruption_applied: dict[str, Any] | None
    inference_time_ms: float
