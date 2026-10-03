from pydantic import BaseModel


class InferenceTime(BaseModel):
    classifier_ms: float
    specialist_ms: float
    total_ms: float


class HardRoutedRestoreResponse(BaseModel):
    original_image: str
    restored_image: str
    class_probabilities: dict[str, float]
    predicted_class: str
    selected_expert: str
    inference_time: InferenceTime
