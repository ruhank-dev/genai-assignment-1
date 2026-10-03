"""Upload validation, resize/normalise to NCHW float32 [0,1], PNG data-URL encoding, heat-map colouring."""
import base64
import io

import numpy as np
from fastapi import HTTPException, UploadFile
from PIL import Image, UnidentifiedImageError

from src.app.backend.config import settings

ALLOWED_TYPES = {"image/jpeg", "image/png"}
# inferno-like anchors (value 0..1 -> RGB) shared by every heat map (frontend legend uses the same colours)
_ANCHORS = np.array([[0, 0, 4], [87, 16, 110], [188, 55, 84], [249, 142, 9], [252, 255, 164]], dtype=np.float32)


async def read_upload(file: UploadFile) -> Image.Image:
    """Validate type (JPEG/PNG), size (<= max_upload_mb) and decodability; returns an RGB image. Never uses the filename."""
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(400, f"Unsupported file type '{file.content_type}'. Upload a JPEG or PNG image.")
    limit = settings.max_upload_mb * 1024 * 1024
    data = await file.read(limit + 1)
    if len(data) > limit:
        raise HTTPException(413, f"File too large (max {settings.max_upload_mb} MB).")
    try:
        img = Image.open(io.BytesIO(data))
        img.load()
    except (UnidentifiedImageError, OSError, Image.DecompressionBombError):
        raise HTTPException(400, "The uploaded file is not a valid image.")
    if min(img.size) < 8 or max(img.size) > 8000:
        raise HTTPException(400, "Image dimensions must be between 8 and 8000 pixels.")
    return img.convert("RGB")


def to_array(img: Image.Image) -> np.ndarray:
    """PIL -> (3, 128, 128) float32 in [0, 1] (bilinear resize, as in the training pipeline)."""
    s = settings.image_size
    return np.asarray(img.resize((s, s), Image.BILINEAR), dtype=np.float32).transpose(2, 0, 1) / 255.0


def to_data_url(chw01: np.ndarray) -> str:
    arr = (np.clip(chw01, 0, 1).transpose(1, 2, 0) * 255 + 0.5).astype(np.uint8)
    buf = io.BytesIO()
    Image.fromarray(arr).save(buf, format="PNG")
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()


def colorize(v01: np.ndarray) -> np.ndarray:
    """(H,W) values in [0,1] -> (3,H,W) inferno-like colours in [0,1]."""
    xs = np.linspace(0, 1, len(_ANCHORS))
    rgb = np.stack([np.interp(np.clip(v01, 0, 1), xs, _ANCHORS[:, c]) for c in range(3)]) / 255.0
    return rgb.astype(np.float32)


def error_map(a: np.ndarray, b: np.ndarray, vmax: float = 0.5) -> np.ndarray:
    """|a-b| averaged over channels, scaled to [0, vmax] and coloured -> (3,H,W)."""
    return colorize(np.abs(a - b).mean(0) / vmax)


def stroke_map(sketch: np.ndarray) -> tuple[np.ndarray, dict]:
    """Heat map of stroke intensity (1 - luminance) of a generated sketch plus simple ink statistics."""
    lum = 0.299 * sketch[0] + 0.587 * sketch[1] + 0.114 * sketch[2]
    ink = np.clip(1.0 - lum, 0, 1)
    return colorize(ink / 0.6), {"mean_ink": float(ink.mean()), "dark_fraction": float((ink > 0.5).mean())}
