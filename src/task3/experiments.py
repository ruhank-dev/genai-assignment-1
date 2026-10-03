"""Step 1 (gate head) and Step 4 (balance regulariser) side-by-side experiments. Real runs, seed 42."""
import argparse
import json

from src.shared.config import settings
from src.task3.train import BASELINE, run_training

OUT = settings.results_dir / "task3"


def summarize(res: dict, name: str, extra: dict) -> dict:
    h = res["history"]
    i = max(range(len(h["val_ssim"])), key=lambda k: h["val_ssim"][k])
    wm = h["w_mean"][-1]
    return {"variant": name, "best_ep": i, "val_psnr": h["val_psnr"][i], "val_ssim": h["val_ssim"][i],
            "val_l1": h["val_l1"][i], "gate_acc": h["val_gate_acc"][-1], "final_w_mean": wm,
            "min_expert_util": min(wm), "max_expert_util": max(wm),
            "collapse": max(wm) > 0.9 or min(wm) < 0.02, **extra}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("which", choices=["gate", "balance"])
    a = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    if a.which == "gate":  # 3 warm-up epochs, experts frozen: does a non-linear head help?
        for head in ("linear", "mlp"):
            r = run_training({**BASELINE, "head_type": head}, 3, 0, settings.checkpoint_dir / "task3" / "exp",
                             f"gate_{head}.pth", "genai-task3-gate-experiment", f"gate-{head}")
            rows.append(summarize(r, head, {}))
            print(rows[-1], flush=True)
        (OUT / "gate_experiment.json").write_text(json.dumps(rows, indent=2))
    else:  # 10 epochs (3 warm-up + 7 joint), same seed/lr, lambda_bal=0.01
        for bal in ("l2", "entropy", "switch"):
            r = run_training({**BASELINE, "balance": bal}, 3, 7, settings.checkpoint_dir / "task3" / "exp",
                             f"bal_{bal}.pth", "genai-task3-balance-experiment", f"balance-{bal}")
            rows.append(summarize(r, bal, {}))
            print(rows[-1], flush=True)
        (OUT / "balance_experiment.json").write_text(json.dumps(rows, indent=2))
