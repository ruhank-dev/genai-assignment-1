"""ONNX Runtime session registry (loaded once at start-up) + the four task pipelines."""
import time

import numpy as np
import onnxruntime as ort
from fastapi import HTTPException

from src.app.backend.config import settings

FILES = {"universal": "task1_universal_ae.onnx", "classifier": "task2_classifier.onnx",
         "salt": "task2_specialist_salt.onnx", "blur": "task2_specialist_blur.onnx",
         "occlusion": "task2_specialist_occlusion.onnx", "soft_moe": "task3_soft_moe.onnx",
         "generator": "task4_generator.onnx"}
CLASSES = ["clean", "salt_and_pepper", "gaussian_blur", "rectangular_occlusion"]
EXPERTS = ["Identity Bypass", "task2_specialist_salt.onnx", "task2_specialist_blur.onnx", "task2_specialist_occlusion.onnx"]
MOE_KEYS = ["identity_clean", "expert_salt", "expert_blur", "expert_occlusion"]


class ModelRegistry:
    def __init__(self) -> None:
        self.sessions: dict[str, ort.InferenceSession] = {}
        avail = ort.get_available_providers()
        self.providers = [p for p in ("CUDAExecutionProvider", "CPUExecutionProvider") if p in avail]

    def load(self) -> None:
        for name, fn in FILES.items():
            path = settings.model_dir / fn
            if path.exists():
                self.sessions[name] = ort.InferenceSession(str(path), providers=self.providers)

    def loaded(self) -> dict[str, bool]:
        return {name: name in self.sessions for name in FILES}

    def run(self, name: str, feed: dict) -> tuple[list[np.ndarray], float]:
        """Run a model; returns (outputs, milliseconds). 503 with an actionable message if the .onnx file is missing."""
        if name not in self.sessions:
            raise HTTPException(503, f"Model '{FILES[name]}' is not loaded. Place it in '{settings.model_dir}' "
                                     f"and restart the backend.")
        t0 = time.perf_counter_ns()
        out = self.sessions[name].run(None, feed)
        return out, (time.perf_counter_ns() - t0) / 1e6


def universal(reg: ModelRegistry, x: np.ndarray) -> tuple[np.ndarray, float]:
    out, ms = reg.run("universal", {"input": x[None]})
    return out[0][0], ms


def hard_route(reg: ModelRegistry, x: np.ndarray) -> dict:
    """Stage 1 classifier -> argmax -> Stage 2 specialist (or exact identity bypass, 0 ms)."""
    (logits,), cls_ms = reg.run("classifier", {"input": x[None]})
    z = logits[0] - logits[0].max()
    probs = np.exp(z) / np.exp(z).sum()
    r = int(probs.argmax())
    if r == 0:
        restored, spec_ms = x, 0.0
    else:
        out, spec_ms = reg.run(("salt", "blur", "occlusion")[r - 1], {"input": x[None]})
        restored = out[0][0]
    return {"restored": restored, "probs": {c: float(p) for c, p in zip(CLASSES, probs)}, "predicted": CLASSES[r],
            "expert": EXPERTS[r], "classifier_ms": cls_ms, "specialist_ms": spec_ms, "total_ms": cls_ms + spec_ms}


def soft_moe(reg: ModelRegistry, x: np.ndarray) -> tuple[np.ndarray, np.ndarray, float]:
    (img, w), ms = reg.run("soft_moe", {"input_image": x[None]})
    return img[0], w[0], ms


def sketch(reg: ModelRegistry, x: np.ndarray, style_idx: int) -> tuple[np.ndarray, float]:
    """x in [0,1]; the generator works in [-1,1]. Returns the sketch in [0,1]."""
    (out,), ms = reg.run("generator", {"photo": (x[None] * 2 - 1).astype(np.float32),
                                       "style_index": np.array([style_idx], dtype=np.int64)})
    return (out[0] + 1) / 2, ms
