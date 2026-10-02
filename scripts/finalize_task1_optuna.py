"""Close any interrupted trial, export the Task 1 study and write best_hyperparams.json."""
import json

import optuna

from src.shared.config import settings
from src.shared.optuna_utils import create_or_load_study, export_study
from src.task1.optuna_search import to_cfg

s = create_or_load_study("task1-universal-ae", "minimize")
for t in s.trials:
    if t.state.name == "RUNNING":
        s.tell(t.number, state=optuna.trial.TrialState.FAIL)
        print("marked interrupted trial as FAIL:", t.number)
out = settings.results_dir / "task1"
export_study(s, out)
p = s.best_params
(out / "best_hyperparams.json").write_text(json.dumps(
    {"value": s.best_value, "trial": s.best_trial.number, "params": p, "config": to_cfg(p)}, indent=2))
for t in s.trials:
    v = None if t.value is None else round(t.value, 4)
    print(t.number, t.state.name, v, {k: (round(x, 4) if isinstance(x, float) else x) for k, x in t.params.items()})
print("BEST", s.best_value, p)
