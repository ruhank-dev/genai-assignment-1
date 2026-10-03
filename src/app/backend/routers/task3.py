from typing import Annotated

from fastapi import APIRouter, File, Request, UploadFile

from src.app.backend.schemas.task3 import SoftMoERestoreResponse
from src.app.backend.services import inference
from src.app.backend.services.metrics import all_metrics
from src.app.backend.services.preprocessing import error_map, read_upload, to_array, to_data_url

router = APIRouter(prefix="/api/v1/restore")


@router.post("/soft-moe", response_model=SoftMoERestoreResponse)
async def restore_soft_moe(request: Request, image: Annotated[UploadFile, File()],
                           reference: Annotated[UploadFile | None, File()] = None) -> SoftMoERestoreResponse:
    """`reference` (optional) is the clean image the input was made from; it enables true error maps and metrics."""
    x = to_array(await read_upload(image))
    ref = to_array(await read_upload(reference)) if reference is not None else None
    restored, w, ms = inference.soft_moe(request.app.state.registry, x)
    weights = {k: float(v) for k, v in zip(inference.MOE_KEYS, w)}
    target = ref if ref is not None else x
    return SoftMoERestoreResponse(
        original_image=to_data_url(x), restored_image=to_data_url(restored), routing_weights=weights,
        dominant_expert=max(weights, key=weights.get), inference_time_ms=ms,
        error_map=to_data_url(error_map(restored, target)),
        error_reference="clean_reference" if ref is not None else "input", metrics=all_metrics(restored, target),
        input_metrics=all_metrics(x, ref) if ref is not None else None)
