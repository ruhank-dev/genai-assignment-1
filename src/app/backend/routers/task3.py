from typing import Annotated

from fastapi import APIRouter, File, Request, UploadFile

from src.app.backend.schemas.task3 import SoftMoERestoreResponse
from src.app.backend.services import inference
from src.app.backend.services.preprocessing import read_upload, to_array, to_data_url

router = APIRouter(prefix="/api/v1/restore")


@router.post("/soft-moe", response_model=SoftMoERestoreResponse)
async def restore_soft_moe(request: Request, image: Annotated[UploadFile, File()]) -> SoftMoERestoreResponse:
    x = to_array(await read_upload(image))
    restored, w, ms = inference.soft_moe(request.app.state.registry, x)
    weights = {k: float(v) for k, v in zip(inference.MOE_KEYS, w)}
    return SoftMoERestoreResponse(original_image=to_data_url(x), restored_image=to_data_url(restored),
                                  routing_weights=weights, dominant_expert=max(weights, key=weights.get),
                                  inference_time_ms=ms)
