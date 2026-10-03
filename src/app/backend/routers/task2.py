from typing import Annotated

from fastapi import APIRouter, File, Request, UploadFile

from src.app.backend.schemas.task2 import HardRoutedRestoreResponse, InferenceTime
from src.app.backend.services import inference
from src.app.backend.services.preprocessing import read_upload, to_array, to_data_url

router = APIRouter(prefix="/api/v1/restore")


@router.post("/hard-routed", response_model=HardRoutedRestoreResponse)
async def restore_hard_routed(request: Request, image: Annotated[UploadFile, File()]) -> HardRoutedRestoreResponse:
    x = to_array(await read_upload(image))
    r = inference.hard_route(request.app.state.registry, x)
    return HardRoutedRestoreResponse(
        original_image=to_data_url(x), restored_image=to_data_url(r["restored"]), class_probabilities=r["probs"],
        predicted_class=r["predicted"], selected_expert=r["expert"],
        inference_time=InferenceTime(classifier_ms=r["classifier_ms"], specialist_ms=r["specialist_ms"],
                                     total_ms=r["total_ms"]))
