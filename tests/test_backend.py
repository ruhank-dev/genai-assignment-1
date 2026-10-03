"""Backend API tests (FastAPI TestClient, real ONNX models from models/onnx)."""
import base64
import io
import random

import numpy as np
import pytest
from fastapi.testclient import TestClient
from PIL import Image

from src.app.backend.config import settings
from src.app.backend.main import app
from src.app.backend.services import corruption
from src.app.backend.services.preprocessing import to_array

MODELS = settings.model_dir
pytestmark = pytest.mark.skipif(not (MODELS / "task4_generator.onnx").exists(), reason="ONNX models not present")


def png_bytes(arr_hwc_u8: np.ndarray) -> bytes:
    buf = io.BytesIO()
    Image.fromarray(arr_hwc_u8).save(buf, format="PNG")
    return buf.getvalue()


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="module")
def pet_img() -> np.ndarray:
    """A real clean 128x128 pet photo (HWC uint8) from the dataset."""
    from src.shared.datasets.pets import PetDataset
    x = PetDataset(split="test")[5]
    return (x.permute(1, 2, 0).numpy() * 255).round().astype(np.uint8)


def post(client, url, arr, **data):
    return client.post(url, files={"image": ("x.png", png_bytes(arr), "image/png")}, data=data)


def decode(url: str) -> Image.Image:
    assert url.startswith("data:image/png;base64,")
    return Image.open(io.BytesIO(base64.b64decode(url.split(",", 1)[1])))


def as_u8(chw: np.ndarray) -> np.ndarray:
    return (chw.transpose(1, 2, 0) * 255).round().astype(np.uint8)


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200 and r.json()["status"] == "ok" and all(r.json()["models_loaded"].values())
    assert client.get("/docs").status_code == 200


def test_universal_with_runtime_corruption(client, pet_img):
    r = post(client, "/api/v1/restore/universal", pet_img, apply_corruption="true", corruption_type="salt_and_pepper", severity="2", seed="1")
    j = r.json()
    assert r.status_code == 200 and j["corruption_applied"]["p"] == 0.08 and j["error_reference"] == "clean_upload"
    assert decode(j["restored_image"]).size == (128, 128) and decode(j["error_map"]).size == (128, 128)
    assert 0 < j["inference_time_ms"] < 1000
    assert decode(j["corrupted_image"]).tobytes() != decode(j["original_image"]).tobytes()


def test_universal_uploaded_corrupted_image(client, pet_img):
    j = post(client, "/api/v1/restore/universal", pet_img).json()
    assert j["corruption_applied"] is None and j["error_reference"] == "input"


def test_universal_bad_corruption_type(client, pet_img):
    assert post(client, "/api/v1/restore/universal", pet_img, apply_corruption="true", corruption_type="nope").status_code == 422


@pytest.mark.parametrize("kind,expected", [("salt_and_pepper", "salt_and_pepper"), ("gaussian_blur", "gaussian_blur"),
                                           ("rectangular_occlusion", "rectangular_occlusion")])
def test_hard_routed_routes_each_corruption(client, pet_img, kind, expected):
    x = to_array(Image.fromarray(pet_img))
    bad, _ = corruption.apply(x, kind, 3, seed=3)
    j = post(client, "/api/v1/restore/hard-routed", as_u8(bad)).json()
    assert j["predicted_class"] == expected and j["selected_expert"] != "Identity Bypass"
    assert j["inference_time"]["specialist_ms"] > 0 and abs(sum(j["class_probabilities"].values()) - 1) < 1e-5


def test_hard_routed_clean_identity_bypass(client, pet_img):
    j = post(client, "/api/v1/restore/hard-routed", pet_img).json()
    assert j["predicted_class"] == "clean" and j["selected_expert"] == "Identity Bypass"
    assert j["inference_time"]["specialist_ms"] == 0.0
    assert decode(j["restored_image"]).tobytes() == decode(j["original_image"]).tobytes()  # exact bypass


def test_soft_moe_weights(client, pet_img):
    x = to_array(Image.fromarray(pet_img))
    bad, _ = corruption.apply(x, "gaussian_blur", 3, seed=1)
    j = post(client, "/api/v1/restore/soft-moe", as_u8(bad)).json()
    w = j["routing_weights"]
    assert abs(sum(w.values()) - 1.0) < 1e-5 and j["dominant_expert"] == max(w, key=w.get) == "expert_blur"


def test_sketch_styles_differ(client, pet_img):
    outs = []
    for s in (1, 2, 3):
        j = post(client, "/api/v1/sketch/generate", pet_img, style=str(s)).json()
        assert j["selected_style"] == s and j["style_description"].startswith(f"FS2K Style {s}")
        outs.append(decode(j["sketch_image"]).tobytes())
    assert len(set(outs)) == 3
    assert post(client, "/api/v1/sketch/generate", pet_img, style="4").status_code == 422


def test_upload_validation(client, pet_img):
    r = client.post("/api/v1/restore/hard-routed", files={"image": ("a.txt", b"hello", "text/plain")})
    assert r.status_code == 400
    r = client.post("/api/v1/restore/hard-routed", files={"image": ("a.png", b"not an image", "image/png")})
    assert r.status_code == 400
    big = png_bytes(np.random.default_rng(0).integers(0, 255, (2200, 2200, 3), dtype=np.uint8))
    assert len(big) > 10 * 1024 * 1024
    r = client.post("/api/v1/restore/hard-routed", files={"image": ("big.png", big, "image/png")})
    assert r.status_code == 413


def test_missing_model_gives_503(tmp_path, pet_img, monkeypatch):
    monkeypatch.setattr(settings, "model_dir", tmp_path)
    old = getattr(app.state, "registry", None)  # the lifespan below replaces the shared app's registry
    with TestClient(app) as c:
        assert c.get("/health").json()["status"] == "degraded"
        r = post(c, "/api/v1/restore/soft-moe", pet_img)
        assert r.status_code == 503 and "task3_soft_moe.onnx" in r.json()["detail"]
    if old is not None:
        app.state.registry = old


def test_numpy_corruptions_match_training_implementation():
    """The backend's numpy corruptions must agree with the torch ones used for training/evaluation."""
    import torch
    from src.shared.corruptions import apply_corruption
    rng = np.random.default_rng(0)
    x = rng.random((3, 128, 128), dtype=np.float32)
    for k, s in corruption.BLUR_LEVELS:
        ref = apply_corruption(torch.from_numpy(x), {"type": "blur", "k": k, "sigma": s}).numpy()
        assert np.allclose(corruption.gaussian_blur(x, k, s), ref, atol=1e-5)
    y = corruption.salt_pepper(np.full((3, 128, 128), 0.5, np.float32), 0.15, np.random.default_rng(1))
    assert abs(((y == 0) | (y == 1)).mean() - 0.15) < 0.01
    for (n, f) in corruption.OCC_LEVELS:
        cov = np.mean([(corruption.occlusion(np.ones((3, 128, 128), np.float32), n, f, random.Random(i))[0] == 0).mean() for i in range(30)])
        assert abs(cov - f) < 0.03


def test_numpy_metrics_match_training_metrics():
    import torch
    from src.app.backend.services.metrics import psnr as np_psnr, ssim as np_ssim
    from src.shared.metrics import psnr_per_image, ssim_per_image
    rng = np.random.default_rng(0)
    a = rng.random((3, 128, 128), dtype=np.float32)
    b = np.clip(a + rng.normal(0, 0.05, a.shape), 0, 1).astype(np.float32)
    ta, tb = torch.from_numpy(a)[None], torch.from_numpy(b)[None]
    assert abs(np_psnr(b, a) - float(psnr_per_image(ta, tb))) < 1e-3
    assert abs(np_ssim(b, a) - float(ssim_per_image(ta, tb))) < 1e-4


def test_every_endpoint_returns_a_heat_map_and_metrics(client, pet_img):
    x = to_array(Image.fromarray(pet_img))
    bad, _ = corruption.apply(x, "salt_and_pepper", 3, seed=2)
    files = {"image": ("c.png", png_bytes(as_u8(bad)), "image/png"), "reference": ("r.png", png_bytes(pet_img), "image/png")}
    for url in ("/api/v1/restore/hard-routed", "/api/v1/restore/soft-moe"):
        j = client.post(url, files=files).json()
        assert j["error_reference"] == "clean_reference" and decode(j["error_map"]).size == (128, 128)
        assert j["input_metrics"]["psnr"] < j["metrics"]["psnr"]  # restoration beats the corrupted input vs. the clean reference
        j2 = post(client, url, as_u8(bad)).json()  # without a reference: compared with the input
        assert j2["error_reference"] == "input" and j2["input_metrics"] is None
    u = post(client, "/api/v1/restore/universal", pet_img, apply_corruption="true", corruption_type="salt_and_pepper", severity="3").json()
    assert u["input_metrics"]["psnr"] < u["metrics"]["psnr"] and 0 < u["metrics"]["ssim"] <= 1
    s = post(client, "/api/v1/sketch/generate", pet_img, style="2").json()
    assert s["error_reference"] == "stroke_intensity" and decode(s["error_map"]).size == (128, 128)
    assert 0 <= s["stats"]["mean_ink"] <= 1 and 0 <= s["stats"]["dark_fraction"] <= 1


def test_forced_identity_bypass(client, pet_img):
    x = to_array(Image.fromarray(pet_img))
    bad, _ = corruption.apply(x, "gaussian_blur", 3, seed=1)
    j = post(client, "/api/v1/restore/hard-routed", as_u8(bad), force_bypass="true").json()
    assert j["forced_bypass"] and j["selected_expert"] == "Identity Bypass" and j["inference_time"]["specialist_ms"] == 0.0
    assert j["predicted_class"] == "gaussian_blur"  # classifier still reports its own opinion
    assert decode(j["restored_image"]).tobytes() == decode(j["original_image"]).tobytes()
