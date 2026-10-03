from pydantic import BaseModel


class SketchStats(BaseModel):
    mean_ink: float  # mean stroke intensity (1 - luminance) of the generated sketch
    dark_fraction: float  # share of pixels with stroke intensity > 0.5


class SketchGenerateResponse(BaseModel):
    original_image: str
    sketch_image: str
    selected_style: int
    style_description: str
    inference_time_ms: float
    error_map: str  # stroke-intensity heat map (no ground-truth sketch exists for user photos)
    error_reference: str  # always "stroke_intensity"
    stats: SketchStats
