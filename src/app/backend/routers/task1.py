from typing import Annotated

from fastapi import APIRouter, File, Form, HTTPException, Request, UploadFile

from src.app.backend.schemas.task1 import UniversalRestoreResponse
from src.app.backend.services import corruption, inference
from src.app.backend.services.metrics import all_metrics
from src.app.backend.services.preprocessing import error_map, read_upload, to_array, to_data_url

router = APIRouter(prefix="/api/v1/restore")


@router.post("/universal", response_model=UniversalRestoreResponse)
async def restore_universal(request: Request, image: Annotated[UploadFile, File()],
                            apply_corruption: Annotated[bool, Form()] = False,
                            corruption_type: Annotated[str | None, Form()] = None,
                            severity: Annotated[int, Form(ge=1, le=3)] = 2,
                            seed: Annotated[int | None, Form()] = None) -> UniversalRestoreResponse:
    x = to_array(await read_upload(image))
    applied, corrupted = None, x
    if apply_corruption:
        if corruption_type not in corruption.KINDS:
            raise HTTPException(422, f"corruption_type must be one of {list(corruption.KINDS)}")
        corrupted, applied = corruption.apply(x, corruption_type, severity, seed)
    corrupted = corrupted.astype("float32")
    restored, ms = inference.universal(request.app.state.registry, corrupted)
    ref = x if apply_corruption else corrupted
    return UniversalRestoreResponse(
        original_image=to_data_url(x), corrupted_image=to_data_url(corrupted), restored_image=to_data_url(restored),
        error_map=to_data_url(error_map(restored, ref)),
        error_reference="clean_upload" if apply_corruption else "input", corruption_applied=applied,
        inference_time_ms=ms, metrics=all_metrics(restored, ref),
        input_metrics=all_metrics(corrupted, x) if apply_corruption else None)
