import argparse
import json

import optuna

from src.shared.config import settings
from src.shared.optuna_utils import create_or_load_study, export_study
from src.task1.train import train_model

CH = {"s": [32, 64, 128], "m": [64, 128, 256], "l": [32, 64, 128, 256]}


def to_cfg(p: dict) -> dict:
    return dict(lr=p["learning_rate"], batch_size=p["batch_size"], bottleneck_dim=p["bottleneck_dim"],
                channels=CH[p["encoder_channels"]], dropout=p["dropout"], alpha=p["alpha"], weight_decay=1e-4)


STUDY = "task1-universal-ae-constrained"
MIN_RATIO = 2.0  # genuine compression required by the assignment: input values / latent values >= 2


def ratio(p: dict) -> float:
    sp = 128 // 2 ** len(CH[p["encoder_channels"]])
    return 3 * 128 * 128 / (p["bottleneck_dim"] * sp * sp)


def objective(trial: optuna.Trial, epochs: int) -> float:
    p = dict(learning_rate=trial.suggest_float("learning_rate", 1e-4, 1e-2, log=True),
             batch_size=trial.suggest_categorical("batch_size", [16, 32, 64]),
             bottleneck_dim=trial.suggest_categorical("bottleneck_dim", [64, 128, 256, 512]),
             encoder_channels=trial.suggest_categorical("encoder_channels", list(CH)),
             dropout=trial.suggest_float("dropout", 0.0, 0.5), alpha=trial.suggest_float("alpha", 0.5, 1.0))
    if ratio(p) < MIN_RATIO:  # infeasible: latent is not a real bottleneck -> skip without training
        trial.set_user_attr("trained", False)
        raise optuna.TrialPruned()
    trial.set_user_attr("trained", True)
    r = train_model(to_cfg(p), epochs, settings.checkpoint_dir / "task1" / "optuna", f"trial_{trial.number}.pth",
                    "genai-task1-universal-ae", f"trial-{trial.number}", trial=trial, patience=100,
                    log_images=False, tags={"optuna_trial": str(trial.number)})
    return r["best_val_objective"]


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--trials", type=int, default=30)
    ap.add_argument("--epochs", type=int, default=20)
    a = ap.parse_args()
    # Direction: minimize L1 + (1 - SSIM) on the val manifest (alpha-independent so trials are comparable).
    study = create_or_load_study(STUDY, "minimize", n_startup=5, n_warmup=5)
    while sum(t.user_attrs.get("trained", False) and t.state.is_finished() for t in study.trials) < a.trials:
        study.optimize(lambda t: objective(t, a.epochs), n_trials=1)
    out = settings.results_dir / "task1"
    export_study(study, out)
    p = dict(study.best_params)
    best = {"value": study.best_value, "trial": study.best_trial.number, "params": p, "config": to_cfg(p)}
    (out / "best_hyperparams.json").write_text(json.dumps(best, indent=2))
    print("best", study.best_value, p)
