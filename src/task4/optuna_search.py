import argparse
import json

import optuna

from src.shared.config import settings
from src.shared.optuna_utils import create_or_load_study, export_study
from src.task4.train import BASELINE, train_gan


def to_cfg(p: dict) -> dict:
    return {**BASELINE, "g_lr": p["g_lr"], "d_lr": p["d_lr"], "batch_size": p["batch_size"], "base": p["base_channels"],
            "dropout": p["dropout"], "emb_dim": p["style_embed_dim"], "lambda_l1": p["lambda_l1"]}


def objective(trial: optuna.Trial, epochs: int) -> float:
    p = dict(g_lr=trial.suggest_float("g_lr", 1e-4, 2e-3, log=True), d_lr=trial.suggest_float("d_lr", 1e-4, 2e-3, log=True),
             batch_size=trial.suggest_categorical("batch_size", [4, 8, 16]),
             base_channels=trial.suggest_categorical("base_channels", [32, 64]),
             dropout=trial.suggest_float("dropout", 0.0, 0.5),
             style_embed_dim=trial.suggest_categorical("style_embed_dim", [8, 16, 32]),
             lambda_l1=trial.suggest_float("lambda_l1", 10.0, 200.0, log=True))
    # non-finite losses raise TrialPruned inside train_gan
    r = train_gan(to_cfg(p), epochs, settings.checkpoint_dir / "task4" / "optuna", f"trial{trial.number}_",
                  "genai-task4-cgan", f"trial-{trial.number}", trial=trial, grid_every=0,
                  tags={"optuna_trial": str(trial.number)})
    return r["best_val_l1"]


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--trials", type=int, default=10)
    ap.add_argument("--epochs", type=int, default=20)
    a = ap.parse_args()
    # minimize validation L1 (fast, correlated with identity/geometry retention); MedianPruner(5, 5 warm-up, every 5)
    study = create_or_load_study("task4-cgan", "minimize", n_startup=5, n_warmup=5, interval_steps=5)
    done = len([t for t in study.trials if t.state.is_finished()])
    study.optimize(lambda t: objective(t, a.epochs), n_trials=max(0, a.trials - done))
    out = settings.results_dir / "task4"
    export_study(study, out)
    p = study.best_params
    (out / "optuna_best_params.json").write_text(json.dumps(
        {"value": study.best_value, "trial": study.best_trial.number, "params": p, "config": to_cfg(p)}, indent=2))
    print("best", study.best_value, p)
