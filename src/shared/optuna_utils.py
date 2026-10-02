"""Uniform Optuna study factory (SQLite, TPE seed 42, MedianPruner) + exporter."""
import json
import sqlite3
from pathlib import Path

import optuna

from src.shared.config import settings

optuna.logging.set_verbosity(optuna.logging.WARNING)


def storage_url() -> str:
    settings.optuna_dir.mkdir(exist_ok=True, parents=True)
    return f"sqlite:///{(settings.optuna_dir / 'optuna_studies.db').as_posix()}"


def _enable_wal() -> None:
    con = sqlite3.connect(settings.optuna_dir / "optuna_studies.db", timeout=30)
    con.execute("PRAGMA journal_mode=WAL")
    con.close()


def create_or_load_study(study_name: str, direction: str, n_startup: int = 5, n_warmup: int = 3,
                         seed: int = 42, interval_steps: int = 1) -> optuna.Study:
    study = optuna.create_study(
        study_name=study_name, storage=storage_url(), direction=direction, load_if_exists=True,
        sampler=optuna.samplers.TPESampler(seed=seed),
        pruner=optuna.pruners.MedianPruner(n_startup_trials=n_startup, n_warmup_steps=n_warmup,
                                           interval_steps=interval_steps),
    )
    _enable_wal()
    return study


def export_study(study: optuna.Study, out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    df = study.trials_dataframe()
    df.to_csv(out_dir / f"{study.study_name}_trials.csv", index=False)
    complete = [t for t in study.trials if t.state == optuna.trial.TrialState.COMPLETE]
    best = {"best_value": study.best_value, "best_params": study.best_params, "best_trial": study.best_trial.number,
            "n_trials": len(study.trials), "n_complete": len(complete),
            "n_pruned": sum(t.state == optuna.trial.TrialState.PRUNED for t in study.trials)} if complete else {}
    (out_dir / f"{study.study_name}_best.json").write_text(json.dumps(best, indent=2))
