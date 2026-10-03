from pydantic import BaseModel


class SketchGenerateResponse(BaseModel):
    original_image: str
    sketch_image: str
    selected_style: int
    style_description: str
    inference_time_ms: float
