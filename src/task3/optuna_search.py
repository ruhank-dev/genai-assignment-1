import argparse
import json

import optuna

from src.shared.config import settings
from src.shared.optuna_utils import create_or_load_study, export_study
from src.task3.train import BASELINE, run_training


def objective(trial: optuna.Trial, warmup: int, joint: int, balance: str) -> float:
    cfg = {**BASELINE, "balance": balance,
           "fine_tune_lr": trial.suggest_float("fine_tune_lr", 1e-5, 1e-3, log=True),
           "tau": trial.suggest_float("temperature", 0.1, 5.0),
           "lam_ce": trial.suggest_float("lambda_ce", 0.01, 0.5, log=True),
           "lam_bal": trial.suggest_float("lambda_balance", 0.001, 0.1, log=True),
           "alpha": trial.suggest_float("reconstruction_alpha", 0.5, 1.0)}
    r = run_training(cfg, warmup, joint, settings.checkpoint_dir / "task3" / "optuna", f"trial_{trial.number}.pth",
                     "genai-task3-soft-moe", f"trial-{trial.number}", trial=trial, collapse_prune=True,
                     tags={"optuna_trial": str(trial.number)})
    return r["best_val_ssim"]


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--trials", type=int, default=10)
    ap.add_argument("--warmup", type=int, default=2)
    ap.add_argument("--joint", type=int, default=6)
    ap.add_argument("--balance", default="l2")
    a = ap.parse_args()
    # maximize validation SSIM; pruners: MedianPruner(5 startup, 3 warm-up) + routing-collapse rule (joint phase)
    study = create_or_load_study("task3-moe-joint", "maximize", n_startup=5, n_warmup=3)
    done = len([t for t in study.trials if t.state.is_finished()])
    study.optimize(lambda t: objective(t, a.warmup, a.joint, a.balance), n_trials=max(0, a.trials - done))
    out = settings.results_dir / "task3"
    export_study(study, out)
    p = study.best_params
    cfg = {**BASELINE, "balance": a.balance, "fine_tune_lr": p["fine_tune_lr"], "tau": p["temperature"],
           "lam_ce": p["lambda_ce"], "lam_bal": p["lambda_balance"], "alpha": p["reconstruction_alpha"]}
    best = {"value": study.best_value, "trial": study.best_trial.number, "params": p, "config": cfg}
    (out / "best_params.json").write_text(json.dumps(best, indent=2))
    cfg_dir = settings.results_dir.parent / "config"
    cfg_dir.mkdir(exist_ok=True)
    (cfg_dir / "task3_best_params.json").write_text(json.dumps(best, indent=2))
    print("best", study.best_value, p)
