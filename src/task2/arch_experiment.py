"""Step-1 side-by-side: custom conv stacks vs ImageNet-pretrained ResNet-18 (3 epochs, same data/seed)."""
import json
import time

import torch

from src.shared.config import get_device, settings
from src.task2.train_classifier import BASELINE, build_classifier, train_classifier

if __name__ == "__main__":
    rows = []
    for name, cfg in (("custom-small", {**BASELINE, "channel_config": "small"}),
                      ("custom-medium", BASELINE), ("custom-large", {**BASELINE, "channel_config": "large"}),
                      ("resnet18-pretrained", {**BASELINE, "arch": "resnet18", "lr": 3e-4})):
        r = train_classifier(cfg, 3, settings.checkpoint_dir / "task2" / "arch_exp" / f"{name}.pt",
                             "genai-task2-arch-experiment", name)
        m = build_classifier(cfg).to(get_device()).eval()
        x = torch.rand(1, 3, 128, 128, device=get_device())
        with torch.no_grad():
            for _ in range(20):
                m(x)
            torch.cuda.synchronize()
            t0 = time.perf_counter()
            for _ in range(100):
                m(x)
            torch.cuda.synchronize()
        rows.append({"model": name, "params": sum(p.numel() for p in m.parameters()), "macro_f1": r["best_macro_f1"],
                     "accuracy": r["metrics"]["accuracy"], "latency_ms_gpu_b1": round(10 * (time.perf_counter() - t0), 3)})
        print(rows[-1], flush=True)
    out = settings.results_dir / "task2"
    out.mkdir(parents=True, exist_ok=True)
    (out / "arch_experiment.json").write_text(json.dumps(rows, indent=2))
