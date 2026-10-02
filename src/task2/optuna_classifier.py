import argparse
import json

import optuna

from src.shared.config import settings
from src.shared.optuna_utils import create_or_load_study, export_study
from src.task2.train_classifier import train_classifier


def objective(trial: optuna.Trial, epochs: int) -> float:
    cfg = dict(lr=trial.suggest_float("learning_rate", 1e-4, 1e-2, log=True),
               batch_size=trial.suggest_categorical("batch_size", [16, 32, 64]),
               channel_config=trial.suggest_categorical("channel_config", ["small", "medium", "large"]),
               dropout=trial.suggest_float("dropout", 0.0, 0.5, step=0.05),
               weight_decay=trial.suggest_float("weight_decay", 1e-5, 1e-2, log=True))
    path = settings.checkpoint_dir / "task2" / "optuna" / f"cls_trial_{trial.number}.pt"
    r = train_classifier(cfg, epochs, path, "genai-task2-classifier", f"trial-{trial.number}", trial=trial,
                         tags={"optuna_trial": str(trial.number)})
    return r["best_macro_f1"]


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--trials", type=int, default=20)
    ap.add_argument("--epochs", type=int, default=10)
    a = ap.parse_args()
    study = create_or_load_study("task2-classifier", "maximize", n_startup=5, n_warmup=3)  # maximize val macro-F1
    done = len([t for t in study.trials if t.state.is_finished()])
    study.optimize(lambda t: objective(t, a.epochs), n_trials=max(0, a.trials - done))
    out = settings.results_dir / "task2"
    export_study(study, out)
    p = study.best_params
    cfg = dict(lr=p["learning_rate"], batch_size=p["batch_size"], channel_config=p["channel_config"],
               dropout=p["dropout"], weight_decay=p["weight_decay"])
    best = {"value": study.best_value, "trial": study.best_trial.number, "params": p, "config": cfg}
    (out / "classifier_best_params.json").write_text(json.dumps(best, indent=2))
    print("best", study.best_value, p)
