from typing import Annotated

from fastapi import APIRouter, File, Form, Request, UploadFile

from src.app.backend.schemas.task2 import HardRoutedRestoreResponse, InferenceTime
from src.app.backend.services import inference
from src.app.backend.services.metrics import all_metrics
from src.app.backend.services.preprocessing import error_map, read_upload, to_array, to_data_url

router = APIRouter(prefix="/api/v1/restore")


@router.post("/hard-routed", response_model=HardRoutedRestoreResponse)
async def restore_hard_routed(request: Request, image: Annotated[UploadFile, File()],
                              reference: Annotated[UploadFile | None, File()] = None,
                              force_bypass: Annotated[bool, Form()] = False) -> HardRoutedRestoreResponse:
    """`reference` (optional) is the clean image the input was made from; it enables true error maps and metrics."""
    x = to_array(await read_upload(image))
    ref = to_array(await read_upload(reference)) if reference is not None else None
    r = inference.hard_route(request.app.state.registry, x, force_bypass)
    target = ref if ref is not None else x
    return HardRoutedRestoreResponse(
        original_image=to_data_url(x), restored_image=to_data_url(r["restored"]), class_probabilities=r["probs"],
        predicted_class=r["predicted"], selected_expert=r["expert"],
        inference_time=InferenceTime(classifier_ms=r["classifier_ms"], specialist_ms=r["specialist_ms"],
                                     total_ms=r["total_ms"]),
        error_map=to_data_url(error_map(r["restored"], target)),
        error_reference="clean_reference" if ref is not None else "input", metrics=all_metrics(r["restored"], target),
        input_metrics=all_metrics(x, ref) if ref is not None else None, forced_bypass=force_bypass)
