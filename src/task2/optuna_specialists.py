"""Shared Optuna search: one architecture/hyper-parameter set evaluated on a mixed (salt+blur+occlusion) task."""
import argparse
import json

import optuna

from src.shared.config import settings
from src.shared.optuna_utils import create_or_load_study, export_study
from src.task1.train import train_model
from src.task2.specialist import CHANNELS, SPEC_TYPES
from src.task2.train_specialists import spec_cfg

MIN_RATIO = 2.0  # same genuine-bottleneck rule as Task 1


def ratio(p: dict) -> float:
    sp = 128 // 2 ** len(CHANNELS[p["channel_config"]])
    return 3 * 128 * 128 / (p["bottleneck_dim"] * sp * sp)


def objective(trial: optuna.Trial, epochs: int) -> float:
    p = dict(learning_rate=trial.suggest_float("learning_rate", 1e-4, 1e-2, log=True),
             bottleneck_dim=trial.suggest_categorical("bottleneck_dim", [64, 128, 256]),
             channel_config=trial.suggest_categorical("channel_config", list(CHANNELS)),
             batch_size=trial.suggest_categorical("batch_size", [16, 32, 64]),
             alpha=trial.suggest_float("alpha", 0.5, 1.0, step=0.05))
    if ratio(p) < MIN_RATIO:
        trial.set_user_attr("trained", False)
        raise optuna.TrialPruned()
    trial.set_user_attr("trained", True)
    r = train_model(spec_cfg(p), epochs, settings.checkpoint_dir / "task2" / "optuna", f"spec_trial_{trial.number}.pt",
                    "genai-task2-specialists", f"trial-{trial.number}", types=SPEC_TYPES, trial=trial, patience=100,
                    log_images=False, tags={"optuna_trial": str(trial.number)})
    return r["best_val_objective"]


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--trials", type=int, default=12)
    ap.add_argument("--epochs", type=int, default=10)
    a = ap.parse_args()
    # minimize L1 + (1 - SSIM) on the balanced salt/blur/occlusion validation manifest
    study = create_or_load_study("task2-specialists", "minimize", n_startup=5, n_warmup=3)
    while sum(t.user_attrs.get("trained", False) and t.state.is_finished() for t in study.trials) < a.trials:
        study.optimize(lambda t: objective(t, a.epochs), n_trials=1)
    out = settings.results_dir / "task2"
    export_study(study, out)
    p = study.best_params
    (out / "specialists_best_params.json").write_text(json.dumps(
        {"value": study.best_value, "trial": study.best_trial.number, "params": p, "config": spec_cfg(p)}, indent=2))
    print("best", study.best_value, p)
