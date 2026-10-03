"""Task 3 test evaluation: Task 1 vs Task 2 (oracle, predicted) vs Task 3 soft MoE on the test manifest."""
import csv
import json
import random

import matplotlib.pyplot as plt
import numpy as np
import torch

from src.shared.config import get_device, settings
from src.shared.corruptions import TYPES
from src.shared.datasets.corrupted import CorruptedPets
from src.shared.evaluation import SEV_NAME, aggregate, score_test
from src.shared.visualization import make_error_heatmap
from src.task1.evaluate import figure, load_model
from src.task2.evaluate import FnModel
from src.task2.inference import load_router
from src.task3.routing_analysis import load_best


def row(name, a, lat):
    s = a["per_severity"]
    g = lambda c: [round(s[f"{c}/{k}"]["psnr"], 2) for k in ("low", "medium", "high")]
    return {"method": name, "overall_psnr": round(a["overall"]["psnr"], 3), "overall_ssim": round(a["overall"]["ssim"], 4),
            "corrupted_psnr": round(a["overall_corrupted"]["psnr"], 3), "corrupted_ssim": round(a["overall_corrupted"]["ssim"], 4),
            "clean_psnr": round(s["clean/-"]["psnr"], 2), "salt_L/M/H": g("salt_pepper"), "blur_L/M/H": g("blur"),
            "occ_L/M/H": g("occlusion"), "latency_ms_per_sample": round(lat, 3)}


if __name__ == "__main__":
    dev = get_device()
    moe, cfg = load_best(dev)
    router = load_router(dev)
    t1, _ = load_model(settings.checkpoint_dir / "task1" / "best_model.pth", dev)
    r1 = score_test(lambda xc, lab: t1(xc))
    ro = score_test(lambda xc, lab: router(xc, oracle_labels=lab)["reconstructed"])
    pr_pred = []

    def pred_fn(xc, lab):
        o = router(xc)
        pr_pred.append(o["routing_decision"].cpu())
        return o["reconstructed"]

    rp = score_test(pred_fn)
    pred = torch.cat(pr_pred).numpy()
    r3 = score_test(lambda xc, lab: moe(xc, cfg["tau"])[0])
    aggs = {"Task 1: Universal AE": (aggregate(r1), r1["ms_per_sample"]),
            "Task 2: Hard (Predicted)": (aggregate(rp), rp["ms_per_sample"]),
            "Task 2: Hard (Oracle)": (aggregate(ro), ro["ms_per_sample"]),
            "Task 3: Soft MoE": (aggregate(r3), r3["ms_per_sample"])}
    table = [row(k, a, l) for k, (a, l) in aggs.items()]
    out = settings.results_dir / "task3"
    fig_dir = out / "figures"
    fig_dir.mkdir(parents=True, exist_ok=True)
    with open(out / "test_benchmark_comparison.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(table[0]))
        w.writeheader()
        w.writerows(table)
    full = {k: a for k, (a, _) in aggs.items()}
    # win/loss per severity: Task 3 vs Task 2 predicted (PSNR)
    wl = {c: {"t3": full["Task 3: Soft MoE"]["per_severity"][c]["psnr"],
              "t2_pred": full["Task 2: Hard (Predicted)"]["per_severity"][c]["psnr"],
              "t1": full["Task 1: Universal AE"]["per_severity"][c]["psnr"]} for c in full["Task 3: Soft MoE"]["per_severity"]}
    (out / "test_metrics.json").write_text(json.dumps({"aggregates": full, "table": table, "per_condition_psnr": wl}, indent=2))
    for t in table:
        print(t)
    for c, v in wl.items():
        print(f"{c:22s} T1 {v['t1']:.2f} T2pred {v['t2_pred']:.2f} T3 {v['t3']:.2f}")
    # qualitative: 12 representative panels (3 per condition)
    ds = CorruptedPets("test")
    rng = random.Random(0)
    idxs, titles = [], []
    for ci, t in enumerate(TYPES):
        for j in range(3):
            sev = 0 if ci == 0 else j + 1
            cand = np.where((r3["label"] == ci) & (r3["sev"] == sev))[0]
            idxs.append(int(rng.choice(list(cand))))
            titles.append(f"{t}\n{SEV_NAME[sev]}")
    moe_fn = FnModel(lambda x: moe(x, cfg["tau"])[0])
    figure_paths = []
    for g in range(0, 12, 3):  # one 3-row figure per condition, then stitched into one 12-panel image
        p = fig_dir / f"_tmp_{g}.png"
        figure(moe_fn, ds, idxs[g:g + 3], titles[g:g + 3], p, dev)
        figure_paths.append(p)
    imgs = [plt.imread(p) for p in figure_paths]
    h = max(i.shape[0] for i in imgs)
    big = np.concatenate([np.pad(i, ((0, h - i.shape[0]), (0, 0), (0, 0)), constant_values=1) for i in imgs], axis=1)
    plt.imsave(fig_dir / "qualitative_comparison_12.png", big)
    for p in figure_paths:
        p.unlink()
    # failure cases: worst T3 PSNR per corrupted type (high severity) + worst-SSIM occlusion
    fi, ft = [], []
    for ci in (3, 1, 2):
        cand = np.where((r3["label"] == ci) & (r3["sev"] == 3))[0]
        w_ = int(cand[np.argmin(r3["psnr"][cand])])
        fi.append(w_)
        ft.append(f"{TYPES[ci]} high\nPSNR {r3['psnr'][w_]:.1f}")
    cand = [c for c in np.where(r3["label"] == 3)[0] if c not in fi]
    w_ = int(min(cand, key=lambda c: r3["ssim"][c]))
    fi.append(w_)
    ft.append(f"occlusion\nSSIM {r3['ssim'][w_]:.2f}")
    figure(moe_fn, ds, fi, ft, fig_dir / "failure_cases_4.png", dev)
    # Task 2 misrouted -> did Task 3 recover? columns: clean | corrupted | T2 (hard) | T3 (soft) | T3 error
    mis = np.where(pred != rp["label"])[0]
    gain = r3["psnr"][mis] - rp["psnr"][mis]
    pick = mis[np.argsort(-gain)[:4]]
    fig, ax = plt.subplots(len(pick), 5, figsize=(11, 2.3 * len(pick)))
    info = []
    for r_, i in enumerate(pick):
        xc, x, lab, sev = ds[int(i)]
        with torch.no_grad():
            y2 = router(xc[None].to(dev))["reconstructed"][0].cpu()
            y3, w3, _ = moe(xc[None].to(dev), cfg["tau"])
        y3 = y3[0].cpu()
        err = make_error_heatmap(y3[None], x[None])[0]
        for a, im, t in zip(ax[r_], (x, xc, y2, y3, err), ("clean", "corrupted", f"T2 hard ({rp['psnr'][i]:.1f} dB)",
                                                         f"T3 soft ({r3['psnr'][i]:.1f} dB)", "T3 |error|")):
            a.imshow(im.permute(1, 2, 0).clamp(0, 1))
            a.axis("off")
            a.set_title(t, fontsize=7)
        ax[r_, 0].text(-0.1, 0.5, f"true {TYPES[lab]} -> T2 routed {TYPES[pred[i]]}", transform=ax[r_, 0].transAxes,
                       rotation=90, va="center", ha="right", fontsize=6)
        info.append({"manifest_idx": int(i), "true": TYPES[lab], "t2_routed": TYPES[pred[i]], "t2_psnr": float(rp["psnr"][i]),
                     "t3_psnr": float(r3["psnr"][i]), "t3_weights": [round(float(v), 3) for v in w3[0].cpu()]})
    fig.tight_layout()
    fig.savefig(fig_dir / "t2_failures_recovered_by_t3.png", dpi=150)
    plt.close(fig)
    frac = float((r3["psnr"][mis] > rp["psnr"][mis]).mean()) if len(mis) else float("nan")
    (out / "t2_misroute_vs_t3.json").write_text(json.dumps({"n_t2_misrouted": int(len(mis)),
                                                            "frac_t3_better_psnr": frac, "top_cases": info}, indent=2))
    print("T2 misrouted", len(mis), "T3 better on", frac, info)
