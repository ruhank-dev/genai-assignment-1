"""Build the figures for the IEEE report from the real result files (training curves, confusion matrix, Optuna histories)
and copy the already generated qualitative figures into report/figures."""
import json
import shutil
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from PIL import Image

R, OUT = Path("results"), Path("report/figures")
OUT.mkdir(parents=True, exist_ok=True)
plt.rcParams.update({"font.size": 8, "axes.grid": True, "grid.alpha": 0.3, "figure.dpi": 150})


def hist(p):
    return json.load(open(p))["history"]


# --- Task 1 training curves (baseline vs final) ---
b, f = hist(R / "task1/baseline_history.json"), hist(R / "task1/final_history.json")
fig, ax = plt.subplots(1, 3, figsize=(7.2, 2.1))
for a, k, t in zip(ax, ("val_loss", "val_psnr", "val_ssim"), ("validation loss", "validation PSNR (dB)", "validation SSIM")):
    a.plot(b[k], label="baseline"), a.plot(f[k], label="final (Optuna)")
    a.set_title(t), a.set_xlabel("epoch")
ax[0].plot(f["train_loss"], "--", color="C1", alpha=0.6, label="final train")
ax[0].legend(fontsize=6)
fig.tight_layout(), fig.savefig(OUT / "t1_curves.pdf"), plt.close(fig)

# --- Task 2 test confusion matrix ---
c = np.array(json.load(open(R / "task2/metrics_summary.json"))["classifier_test"]["confusion_normalized"])
names = ["clean", "salt-pepper", "blur", "occlusion"]
fig, a = plt.subplots(figsize=(3.2, 2.8))
im = a.imshow(c, vmin=0, vmax=1, cmap="Blues")
a.set_xticks(range(4), names, rotation=30, fontsize=7), a.set_yticks(range(4), names, fontsize=7)
for i in range(4):
    for j in range(4):
        a.text(j, i, f"{c[i, j]:.3f}", ha="center", va="center", color="w" if c[i, j] > .5 else "k", fontsize=7)
a.set_xlabel("predicted"), a.set_ylabel("true"), a.grid(False)
fig.tight_layout(), fig.savefig(OUT / "t2_confusion.pdf"), plt.close(fig)

# --- Task 3 validation curve (warm-up | joint) ---
h3 = hist(R / "task3/final_history.json")
fig, ax = plt.subplots(1, 2, figsize=(5.0, 2.0))
ax[0].plot(h3["val_ssim"]), ax[0].axvline(9.5, color="k", ls=":"), ax[0].set_title("validation SSIM (warm-up | joint)")
w = np.array(h3["w_mean"])
for k, n in enumerate(["identity", "salt", "blur", "occlusion"]):
    ax[1].plot(w[:, k], label=n)
ax[1].set_title("mean routing weight on validation"), ax[1].legend(fontsize=5)
for a in ax:
    a.set_xlabel("epoch")
fig.tight_layout(), fig.savefig(OUT / "t3_curves.pdf"), plt.close(fig)

# --- Task 4 GAN losses ---
h4 = hist(R / "task4/final_history.json")
fig, ax = plt.subplots(1, 3, figsize=(7.2, 2.1))
for k in ("d_real_loss", "d_fake_loss", "g_adv_loss"):
    ax[0].plot(h4[k], label=k.replace("_loss", ""))
ax[0].legend(fontsize=6), ax[0].set_title("adversarial losses")
ax[1].plot(h4["g_l1_loss"], label="train"), ax[1].plot(h4["val_l1"], label="val"), ax[1].set_title("L1"), ax[1].legend(fontsize=6)
for s in (1, 2, 3):
    ax[2].plot(h4[f"val_style{s}_l1"], label=f"style {s}")
ax[2].set_title("validation L1 per style"), ax[2].legend(fontsize=6)
for a in ax:
    a.set_xlabel("epoch")
fig.tight_layout(), fig.savefig(OUT / "t4_curves.pdf"), plt.close(fig)

# --- Optuna trial values for the four studies ---
studies = [("Task 1 (constrained)", "task1/task1-universal-ae-constrained_trials.csv", True),
           ("Task 2 classifier", "task2/task2-classifier_trials.csv", False), ("Task 2 specialists", "task2/task2-specialists_trials.csv", True),
           ("Task 3 MoE", "task3/task3-moe-joint_trials.csv", False), ("Task 4 cGAN", "task4/task4-cgan_trials.csv", True)]
fig, ax = plt.subplots(1, 5, figsize=(7.4, 1.9))
for a, (n, p, mn) in zip(ax, studies):
    d = pd.read_csv(R / p)
    if "user_attrs_trained" in d:
        d = d[d["user_attrs_trained"] == True]  # noqa: E712 - infeasible (not trained) trials carry no value
    d = d.reset_index(drop=True)
    done = d[d.state == "COMPLETE"]
    a.scatter(done.index, done.value, s=10, label="complete")
    pr = d[d.state == "PRUNED"]
    a.scatter(pr.index, pr.value, s=10, marker="x", color="r", label="pruned")
    a.plot(done.index, done.value.cummin() if mn else done.value.cummax(), "k-", lw=0.8)
    a.set_title(n, fontsize=6.5), a.set_xlabel("trial")
ax[0].legend(fontsize=5)
fig.tight_layout(), fig.savefig(OUT / "optuna.pdf"), plt.close(fig)

# --- copy existing qualitative figures ---
copy = {"setup/corruption_grid.png": "corruption_grid.png", "task1/visualizations/representative_examples/examples_occlusion.png": "t1_examples_occ.png",
        "task1/visualizations/failure_cases/failure_4.png": "t1_failure.png", "task2/visuals/misroute_1.png": "t2_misroute.png",
        "task3/figures/routing_heatmap.png": "t3_heatmap.png", "task3/figures/severity_routing_trends.png": "t3_trends.png",
        "task3/figures/sharp_vs_distributed_examples.png": "t3_sharp_soft.png", "task3/figures/t2_failures_recovered_by_t3.png": "t3_recovery.png",
        "task4/style_comparison_grid.png": "t4_style_grid.png", "task4/sample_results_grid.png": "t4_samples.png",
        "task4/failure_cases_analysis.png": "t4_failures.png", "app/1_universal.png": "app_universal.png", "app/3_soft_moe.png": "app_softmoe.png",
        "app/4_face_to_sketch.png": "app_sketch.png"}
for s, d in copy.items():  # compact JPEGs (max 1600 px wide) keep the PDF small
    im = Image.open(R / s).convert("RGB")
    im.thumbnail((1600, 1600))
    im.save(OUT / d.replace(".png", ".jpg"), quality=88)
print("figures:", sorted(p.name for p in OUT.iterdir()))
