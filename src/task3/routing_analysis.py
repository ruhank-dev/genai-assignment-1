"""Gate behaviour on the test manifest: 4x4 routing matrix, per-severity weights, heatmap, trends, sharp/soft galleries."""
import csv
import json

import matplotlib.pyplot as plt
import numpy as np
import torch
from torch.utils.data import DataLoader

from src.shared.config import get_device, settings
from src.shared.corruptions import TYPES
from src.shared.datasets.corrupted import CorruptedPets
from src.shared.evaluation import SEV_NAME, SEV_PARAM
from src.task3.train import build_moe

EXPERTS = ["identity", "salt", "blur", "occlusion"]


def load_best(dev):
    ck = torch.load(settings.checkpoint_dir / "task3" / "best_model.pth", map_location=dev)
    m = build_moe(dev, ck["config"].get("head_type", "linear"))
    m.load_state_dict(ck["model_state_dict"])
    return m.eval(), ck["config"]


@torch.no_grad()
def collect(model, tau, dev, split="test"):
    ds = CorruptedPets(split)
    ws = []
    for xc, _, _, _ in DataLoader(ds, 128, num_workers=2):
        ws.append(model(xc.to(dev), tau)[1].cpu())
    man = ds.manifest
    return torch.cat(ws).numpy(), np.array([m["label"] for m in man]), np.array([m["severity"] for m in man])


if __name__ == "__main__":
    dev = get_device()
    model, cfg = load_best(dev)
    w, lab, sev = collect(model, cfg["tau"], dev)
    out = settings.results_dir / "task3"
    fig_dir = out / "figures"
    fig_dir.mkdir(parents=True, exist_ok=True)
    conf = np.stack([w[lab == c].mean(0) for c in range(4)])  # rows: true corruption, cols: expert weight
    with open(out / "routing_confusion_matrix.csv", "w", newline="") as f:
        wr = csv.writer(f)
        wr.writerow(["true\\expert"] + EXPERTS)
        for c in range(4):
            wr.writerow([TYPES[c]] + [f"{v:.4f}" for v in conf[c]])
    rows = []  # per true type and severity
    for c in range(4):
        for s in ((0,) if c == 0 else (1, 2, 3)):
            m = (lab == c) & (sev == s)
            rows.append({"condition": f"{TYPES[c]}/{SEV_NAME[s]}", "params": SEV_PARAM[TYPES[c]][s],
                         **{f"w_{e}": float(w[m][:, k].mean()) for k, e in enumerate(EXPERTS)}})
    with open(out / "routing_by_severity.csv", "w", newline="") as f:
        wr = csv.DictWriter(f, fieldnames=list(rows[0]))
        wr.writeheader()
        wr.writerows(rows)
    # heatmap of the 4x4 matrix + per-severity (10 rows x 4)
    sev_mat = np.array([[r[f"w_{e}"] for e in EXPERTS] for r in rows])
    fig, ax = plt.subplots(1, 2, figsize=(12, 4.5), gridspec_kw={"width_ratios": [1, 1.3]})
    for a, mat, ylab, ttl in ((ax[0], conf, TYPES, "mean routing weight by true corruption"),
                              (ax[1], sev_mat, [r["condition"] for r in rows], "by true corruption / severity")):
        im = a.imshow(mat, vmin=0, vmax=1, cmap="viridis")
        a.set_xticks(range(4), EXPERTS)
        a.set_yticks(range(len(ylab)), ylab, fontsize=8)
        a.set_title(ttl, fontsize=9)
        for i in range(mat.shape[0]):
            for j in range(4):
                a.text(j, i, f"{mat[i, j]:.2f}", ha="center", va="center", color="w" if mat[i, j] < .6 else "k", fontsize=8)
    fig.colorbar(im, ax=ax, fraction=0.025)
    fig.savefig(fig_dir / "routing_heatmap.png", dpi=150, bbox_inches="tight")
    fig.savefig(fig_dir / "routing_heatmap.pdf", bbox_inches="tight")
    plt.close(fig)
    # severity trends: w of the matching expert vs severity
    fig, ax = plt.subplots(1, 3, figsize=(11, 3.2))
    for a, c, name in zip(ax, (1, 2, 3), ("salt-pepper density p", "blur (k, sigma)", "occlusion area")):
        xs = [SEV_PARAM[TYPES[c]][s] for s in (1, 2, 3)]
        for k, e in enumerate(EXPERTS):
            a.plot(xs, [w[(lab == c) & (sev == s)][:, k].mean() for s in (1, 2, 3)], marker="o", label=e)
        a.set_title(name, fontsize=9)
        a.set_ylim(0, 1.02)
        a.tick_params(axis="x", labelsize=7)
    ax[0].set_ylabel("mean weight")
    ax[0].legend(fontsize=7)
    fig.tight_layout()
    fig.savefig(fig_dir / "severity_routing_trends.png", dpi=150)
    fig.savefig(fig_dir / "severity_routing_trends.pdf")
    plt.close(fig)
    # sharp vs soft galleries
    ds = CorruptedPets("test")
    wmax = w.max(1)
    sharp = np.where(wmax > 0.85)[0]
    soft = np.argsort(wmax)[:6]
    sharp_pick = [int(np.where((lab == c) & (wmax > 0.85))[0][3]) for c in range(4)]
    fig, ax = plt.subplots(2, 5, figsize=(12, 5.2))
    for a, i in zip(ax[0], sharp_pick + [int(sharp[100])]):
        a.imshow(ds[i][0].permute(1, 2, 0))
        a.set_title(f"{TYPES[lab[i]]}\n" + " ".join(f"{v:.2f}" for v in w[i]), fontsize=7)
        a.axis("off")
    for a, i in zip(ax[1], soft[:5]):
        a.imshow(ds[int(i)][0].permute(1, 2, 0))
        a.set_title(f"{TYPES[lab[i]]} L{sev[i]}\n" + " ".join(f"{v:.2f}" for v in w[i]), fontsize=7)
        a.axis("off")
    fig.suptitle("top: sharp routing (w_max > 0.85) | bottom: most distributed routing (weights = identity salt blur occ)", fontsize=9)
    fig.savefig(fig_dir / "sharp_vs_distributed_examples.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    # expert health
    mean_all = w.mean(0)
    health = {"mean_weight_overall": dict(zip(EXPERTS, map(float, mean_all))),
              "inactive_experts(<5%)": [e for e, v in zip(EXPERTS, mean_all) if v < 0.05],
              "frac_samples_sharp(w_max>0.85)": float((wmax > 0.85).mean()),
              "frac_samples_soft(w_max<0.6)": float((wmax < 0.6).mean()),
              "wrong_expert_dominance": {f"{TYPES[c]}": {EXPERTS[k]: float((w[lab == c].argmax(1) == k).mean())
                                                        for k in range(4) if k != c} for c in range(4)}}
    (out / "routing_health.json").write_text(json.dumps({"confusion": conf.tolist(), "by_severity": rows, "health": health}, indent=2))
    print(np.round(conf, 4))
    for r in rows:
        print(r["condition"], [round(r[f"w_{e}"], 3) for e in EXPERTS])
    print(json.dumps(health, indent=1))
