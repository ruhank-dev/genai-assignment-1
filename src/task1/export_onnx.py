import json

import torch

from src.shared.config import settings
from src.shared.datasets.corrupted import CorruptedPets
from src.shared.onnx_utils import export_and_verify
from src.shared.tracking import ExperimentTracker
from src.task1.evaluate import load_model

if __name__ == "__main__":
    model, _ = load_model(settings.checkpoint_dir / "task1" / "best_model.pth", torch.device("cpu"))
    ds = CorruptedPets("val")
    x = torch.stack([ds[i][0] for i in range(8)])  # real corrupted validation images
    r = export_and_verify(model, (x,), ["input"], ["output"], settings.onnx_dir / "task1_universal_ae.onnx")
    print(json.dumps(r, indent=2))
    out = settings.results_dir / "task1"
    (out / "onnx_verify.json").write_text(json.dumps(r, indent=2))
    t = ExperimentTracker()
    t.start_run("onnx-verify", "genai-task1-universal-ae")
    t.log_metrics({"max_abs_err_b8": r["max_abs_err"][8], "pytorch_ms": r["pytorch_ms"], "onnx_ms": r["onnxruntime_ms"]}, 0)
    t.end_run()
