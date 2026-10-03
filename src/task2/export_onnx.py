import json

import torch

from src.shared.config import settings
from src.shared.datasets.corrupted import CorruptedPets
from src.shared.onnx_utils import export_and_verify
from src.shared.tracking import ExperimentTracker
from src.task2.inference import load_classifier, load_specialist
from src.task2.specialist import SPEC_FILES, SPEC_TYPES

if __name__ == "__main__":
    cpu = torch.device("cpu")
    d = settings.checkpoint_dir / "task2"
    ds = CorruptedPets("val")
    x = torch.stack([ds[i][0] for i in range(8)])
    results = {}
    results["classifier"] = export_and_verify(load_classifier(d / "classifier_best.pt", cpu), (x,), ["input"], ["logits"],
                                              settings.onnx_dir / "task2_classifier.onnx")
    for t, name in zip(SPEC_TYPES, ("salt", "blur", "occlusion")):
        sp = CorruptedPets("val", types=[t])  # each specialist verified on its own corruption
        xs = torch.stack([sp[i][0] for i in range(8)])
        results[name] = export_and_verify(load_specialist(d / SPEC_FILES[t], cpu), (xs,), ["input"], ["output"],
                                          settings.onnx_dir / f"task2_specialist_{name}.onnx")
    print(json.dumps({k: {"max_abs_err": v["max_abs_err"], "pytorch_ms": v["pytorch_ms"], "onnx_ms": v["onnxruntime_ms"],
                          "size_mb": v["size_mb"]} for k, v in results.items()}, indent=1))
    (settings.results_dir / "task2" / "onnx_verify.json").write_text(json.dumps(results, indent=2))
    t = ExperimentTracker()
    t.start_run("onnx-verify", "genai-task2-classifier")
    t.log_metrics({f"{k}_max_err_b8": v["max_abs_err"][8] for k, v in results.items()}, 0)
    t.end_run()
