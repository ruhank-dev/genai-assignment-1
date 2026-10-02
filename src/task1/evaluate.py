"""Task 1 test evaluation: metric tables, 12 representative examples, 4 failure cases."""
import json
import random

import matplotlib.pyplot as plt
import numpy as np
import torch

from src.shared.config import get_device, settings
from src.shared.corruptions import TYPES
from src.shared.datasets.corrupted import CorruptedPets
from src.shared.evaluation import SEV_NAME, aggregate, score_test
from src.shared.manifests import load
from src.shared.visualization import make_error_heatmap
from src.task1.autoencoder import UniversalAutoencoder


def load_model(path, dev):
    ck = torch.load(path, map_location=dev)
    c = ck["config"]
    m = UniversalAutoencoder(c["channels"], c["bottleneck_dim"], c["dropout"]).to(dev)
    m.load_state_dict(ck["model_state_dict"], strict=True)
    return m.eval(), ck


def panel(model, ds, i, dev, ax_row, title):
    xc, x, lab, sev = ds[i]
    with torch.no_grad():
        y = model(xc[None].to(dev))
    err = make_error_heatmap(y.cpu(), x[None])[0]
    for a, im, t in zip(ax_row, (x, xc, y[0].cpu(), err), ("clean", "corrupted", "restored", "|error| (0-0.5)")):
        a.imshow(im.permute(1, 2, 0).clamp(0, 1))
        a.axis("off")
        a.set_title(t, fontsize=7)
    ax_row[0].text(-0.1, 0.5, title, transform=ax_row[0].transAxes, rotation=90, va="center", ha="right", fontsize=7)


def figure(model, ds, idxs, titles, path, dev):
    fig, ax = plt.subplots(len(idxs), 4, figsize=(8, 2.1 * len(idxs)), squeeze=False)
    for r, (i, t) in enumerate(zip(idxs, titles)):
        panel(model, ds, i, dev, ax[r], t)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


if __name__ == "__main__":
    dev = get_device()
    model, ck = load_model(settings.checkpoint_dir / "task1" / "best_model.pth", dev)
    r = score_test(lambda xc, lab: model(xc))
    res = aggregate(r)
    out = settings.results_dir / "task1"
    rep, fail = out / "visualizations" / "representative_examples", out / "visualizations" / "failure_cases"
    rep.mkdir(parents=True, exist_ok=True)
    fail.mkdir(parents=True, exist_ok=True)
    (out / "metrics_summary.json").write_text(json.dumps(res, indent=2))
    for k, v in res["per_severity"].items():
        print(f"{k:22s} {v['params']:18s} psnr {v['psnr']:.2f} ssim {v['ssim']:.4f} l1 {v['l1']:.4f}")
    print("per-corruption", {k: round(v["psnr"], 2) for k, v in res["per_corruption"].items()})
    print("overall", res["overall"], "ms/sample", res["ms_per_sample"])
    ds = CorruptedPets("test")
    man = load("test_manifest.json")
    rng = random.Random(0)
    idxs, titles = [], []
    for ci, t in enumerate(TYPES):  # 3 examples per condition; severities low/medium/high
        for j in range(3):
            sev = 0 if ci == 0 else j + 1
            cand = np.where((r["label"] == ci) & (r["sev"] == sev))[0]
            idxs.append(int(rng.choice(list(cand))))
            titles.append(f"{t}\n{SEV_NAME[sev]}")
    for g in range(0, 12, 3):
        figure(model, ds, idxs[g:g + 3], titles[g:g + 3], rep / f"examples_{TYPES[g // 3]}.png", dev)
    # failures: worst PSNR per corruption type at high severity + the worst-SSIM occlusion case
    fi, ft = [], []
    for ci in (3, 1, 2):
        cand = np.where((r["label"] == ci) & (r["sev"] == 3))[0]
        w = int(cand[np.argmin(r["psnr"][cand])])
        fi.append(w)
        ft.append(f"{TYPES[ci]} high\nPSNR {r['psnr'][w]:.1f}")
    cand = [c for c in np.where(r["label"] == 3)[0] if c not in fi]
    w = int(min(cand, key=lambda c: r["ssim"][c]))
    fi.append(w)
    ft.append(f"occlusion\nSSIM {r['ssim'][w]:.2f}")
    for n, (i, t) in enumerate(zip(fi, ft)):
        figure(model, ds, [i], [t], fail / f"failure_{n + 1}.png", dev)
    info = [{"manifest_idx": i, "image_idx": man[i]["idx"], "type": man[i]["type"], "severity": man[i]["severity"],
             "psnr": float(r["psnr"][i]), "ssim": float(r["ssim"][i])} for i in fi]
    (out / "failure_cases.json").write_text(json.dumps(info, indent=2))
