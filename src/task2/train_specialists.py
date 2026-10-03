"""Train the 3 specialists independently: each only sees its own corruption, target = clean image."""
import argparse
import json

from src.shared.config import settings
from src.task1.train import train_model
from src.task2.specialist import CHANNELS, SPEC_FILES, SPEC_TYPES

BASELINE = dict(lr=1e-3, batch_size=32, bottleneck_dim=128, channels=CHANNELS["standard"], dropout=0.0, alpha=0.8,
                weight_decay=1e-4)


def spec_cfg(p: dict) -> dict:
    return dict(lr=p["learning_rate"], batch_size=p["batch_size"], bottleneck_dim=p["bottleneck_dim"],
                channels=CHANNELS[p["channel_config"]], dropout=0.0, alpha=p["alpha"], weight_decay=1e-4)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["baseline", "final"], default="baseline")
    ap.add_argument("--epochs", type=int, default=30)
    ap.add_argument("--only", choices=SPEC_TYPES, default=None)
    a = ap.parse_args()
    out = settings.results_dir / "task2"
    out.mkdir(parents=True, exist_ok=True)
    cfg = spec_cfg(json.loads((out / "specialists_best_params.json").read_text())["params"]) \
        if a.mode == "final" else BASELINE
    ck_dir = settings.checkpoint_dir / "task2" / ("baseline" if a.mode == "baseline" else "")
    summary = {}
    for t in ([a.only] if a.only else SPEC_TYPES):
        r = train_model(cfg, a.epochs, ck_dir, SPEC_FILES[t], "genai-task2-specialists", f"{a.mode}-{t}",
                        types=[t], patience=100)
        summary[t] = {"best_val_objective": r["best_val_objective"], "history": r["history"]}
    (out / f"specialists_{a.mode}_history.json").write_text(json.dumps(summary))
    print({t: round(v["best_val_objective"], 4) for t, v in summary.items()})
