from typing import Annotated

from fastapi import APIRouter, File, Form, Request, UploadFile

from src.app.backend.schemas.task4 import SketchGenerateResponse, SketchStats
from src.app.backend.services import inference
from src.app.backend.services.preprocessing import read_upload, stroke_map, to_array, to_data_url

router = APIRouter(prefix="/api/v1/sketch")
# descriptions derived from the observed stroke weight of generated / ground-truth sketches (see task 4 notes)
STYLES = {1: "FS2K Style 1 - fine, light-contour sketch", 2: "FS2K Style 2 - heavy dark-stroke hatching sketch",
          3: "FS2K Style 3 - medium-weight contour sketch"}


@router.post("/generate", response_model=SketchGenerateResponse)
async def generate_sketch(request: Request, image: Annotated[UploadFile, File()],
                          style: Annotated[int, Form(ge=1, le=3)] = 1) -> SketchGenerateResponse:
    x = to_array(await read_upload(image))
    sk, ms = inference.sketch(request.app.state.registry, x, style - 1)
    heat, stats = stroke_map(sk)
    return SketchGenerateResponse(original_image=to_data_url(x), sketch_image=to_data_url(sk), selected_style=style,
                                  style_description=STYLES[style], inference_time_ms=ms, error_map=to_data_url(heat),
                                  error_reference="stroke_intensity", stats=SketchStats(**stats))
