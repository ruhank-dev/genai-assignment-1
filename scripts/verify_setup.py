"""Setup verification: tracker (10 dummy epochs + image), Optuna persistence, dataset/corruption figures."""
import random

import matplotlib.pyplot as plt
import torch

from src.shared.config import get_device, settings
from src.shared.corruptions import TYPES, apply_corruption, sample_params
from src.shared.datasets.fs2k import FS2KDataset
from src.shared.datasets.pets import PetDataset
from src.shared.optuna_utils import create_or_load_study
from src.shared.tracking import ExperimentTracker

out = settings.results_dir / "setup"
print("device", get_device())

# 1. tracker
t = ExperimentTracker()
t.start_run("setup-dummy", "genai-setup-check")
t.log_params({"a": 1})
for e in range(10):
    t.log_metrics({"loss": 1 / (e + 1)}, step=e)
t.log_image("synthetic", torch.rand(3, 64, 64), 0)
t.end_run()
print("tracker ok")

# 2. optuna
import optuna
name = "test-dummy-study"
try:
    optuna.delete_study(study_name=name, storage=__import__("src.shared.optuna_utils", fromlist=["x"]).storage_url())
except KeyError:
    pass
s = create_or_load_study(name, "minimize")
s.optimize(lambda tr: (tr.suggest_float("x", -3, 3) - 1) ** 2, n_trials=3)
s2 = create_or_load_study(name, "minimize")
assert len(s2.trials) == 3 and s2.best_params == s.best_params
print("optuna ok", len(s2.trials), s2.best_params)

# 3. pets samples + corruption grid
ds = PetDataset(split="test", return_labels=True)
idx = random.Random(0).sample(range(len(ds)), 8)
fig, ax = plt.subplots(2, 4, figsize=(10, 5))
for a, i in zip(ax.flat, idx):
    x, l = ds[i]
    a.imshow(x.permute(1, 2, 0)); a.set_title(ds.classes[l][:18], fontsize=8); a.axis("off")
fig.savefig(out / "pets_samples.png", dpi=120)
x = ds[idx[0]][0]
rng = random.Random(1)
cols = [[sample_params("clean", rng)]] + [[sample_params(c, rng, l) for l in (1, 2, 3)] for c in TYPES[1:]]
fig, ax = plt.subplots(4, 4, figsize=(9, 9))
for ci, col in enumerate(cols):
    for r in range(4):
        a = ax[r, ci]; a.axis("off")
        if r < len(col):
            a.imshow(apply_corruption(x, col[r]).permute(1, 2, 0)); a.set_title(f"{col[r]['type']} L{col[r]['severity']}", fontsize=8)
fig.savefig(out / "corruption_grid.png", dpi=120)

# 4. fs2k
d = FS2KDataset("test")
firsts = {}
for i, s in enumerate(d.styles):
    firsts.setdefault(s, i)
fig, ax = plt.subplots(3, 2, figsize=(5, 7))
for r, (s, i) in enumerate(sorted(firsts.items())):
    p, k, _ = d[i]
    ax[r, 0].imshow((p.permute(1, 2, 0) + 1) / 2); ax[r, 1].imshow((k.permute(1, 2, 0) + 1) / 2)
    ax[r, 0].set_title(f"style {s} photo", fontsize=8); ax[r, 1].set_title("sketch", fontsize=8)
    ax[r, 0].axis("off"); ax[r, 1].axis("off")
fig.savefig(out / "fs2k_pairs.png", dpi=120)
print("figures ok")
