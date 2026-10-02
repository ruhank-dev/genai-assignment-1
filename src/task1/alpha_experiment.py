"""Step-2 side-by-side: 5 epochs on a 15% train subset for alpha in {0, .5, .8, 1}."""
import json

from src.shared.config import settings
from src.task1.train import BASELINE, train_model

if __name__ == "__main__":
    rows = []
    for a in (0.0, 0.5, 0.8, 1.0):
        cfg = {**BASELINE, "alpha": a}
        r = train_model(cfg, 5, settings.checkpoint_dir / "task1" / "alpha_exp", f"alpha_{a}.pth",
                        "genai-task1-alpha-experiment", f"alpha-{a}", train_fraction=0.15, log_images=False)
        h = r["history"]
        rows.append({"alpha": a, "val_loss": h["val_loss"][-1], "psnr": h["val_psnr"][-1], "ssim": h["val_ssim"][-1],
                     "l1": h["val_l1"][-1], "objective": h["val_objective"][-1]})
        print(rows[-1], flush=True)
    out = settings.results_dir / "task1"
    out.mkdir(parents=True, exist_ok=True)
    (out / "alpha_experiment.json").write_text(json.dumps(rows, indent=2))
