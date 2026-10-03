"""Combined single-graph export (plan Option A): gate + identity + 3 experts + weighted sum, temperature baked in."""
import json

import torch
import torch.nn as nn

from src.shared.config import settings
from src.shared.datasets.corrupted import CorruptedPets
from src.shared.onnx_utils import export_and_verify
from src.shared.tracking import ExperimentTracker
from src.task3.routing_analysis import load_best


class ExportWrapper(nn.Module):
    def __init__(self, moe, tau: float):
        super().__init__()
        self.moe, self.tau = moe, tau

    def forward(self, x):
        out, w, _ = self.moe(x, self.tau)
        return out, w


if __name__ == "__main__":
    moe, cfg = load_best(torch.device("cpu"))
    ds = CorruptedPets("val")
    x = torch.stack([ds[i][0] for i in range(8)])
    r = export_and_verify(ExportWrapper(moe.cpu().eval(), cfg["tau"]), (x,), ["input_image"],
                          ["restored_image", "routing_weights"], settings.onnx_dir / "task3_soft_moe.onnx")
    print(json.dumps(r, indent=2))
    (settings.results_dir / "task3" / "onnx_verify.json").write_text(json.dumps(r, indent=2))
    t = ExperimentTracker()
    t.start_run("onnx-verify", "genai-task3-soft-moe")
    t.log_metrics({"max_abs_err_b8": r["max_abs_err"][8], "pytorch_ms": r["pytorch_ms"], "onnx_ms": r["onnxruntime_ms"]}, 0)
    t.end_run()
