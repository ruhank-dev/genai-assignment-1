"""Generator-only ONNX: inputs photo (B,3,128,128) float32 + style_index (B,) int64, output sketch (B,3,128,128) in [-1,1]."""
import json

import torch

from src.shared.config import settings
from src.shared.datasets.fs2k import FS2KDataset
from src.shared.onnx_utils import export_and_verify
from src.shared.tracking import ExperimentTracker
from src.task4.generator import UNetGenerator


def load_generator(path, dev=torch.device("cpu")) -> UNetGenerator:
    ck = torch.load(path, map_location=dev)
    c = ck["config"]
    g = UNetGenerator(c["base"], c["emb_dim"], c["dropout"], c["style_mode"]).to(dev)
    g.load_state_dict(ck["model_state_dict"], strict=True)
    return g.eval()


if __name__ == "__main__":
    g = load_generator(settings.checkpoint_dir / "task4" / "best_generator.pth")
    ds = FS2KDataset("val")
    items = [ds[i] for i in range(8)]
    x = torch.stack([i[0] for i in items])
    s = torch.tensor([i[2] for i in items], dtype=torch.int64)
    r = export_and_verify(g, (x, s), ["photo", "style_index"], ["sketch"], settings.onnx_dir / "task4_generator.onnx")
    print(json.dumps(r, indent=2))
    (settings.results_dir / "task4" / "onnx_verify.json").write_text(json.dumps(r, indent=2))
    t = ExperimentTracker()
    t.start_run("onnx-verify", "genai-task4-cgan")
    t.log_metrics({"max_abs_err_b8": r["max_abs_err"][8], "pytorch_ms": r["pytorch_ms"], "onnx_ms": r["onnxruntime_ms"]}, 0)
    t.end_run()
