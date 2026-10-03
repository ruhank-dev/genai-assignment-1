"""Task 2 test evaluation: Task 1 vs oracle-routed vs predicted-routed, classifier test metrics, misrouting audit."""
import csv
import json
import random

import numpy as np
import torch
import torch.nn as nn
from sklearn.metrics import confusion_matrix, precision_recall_fscore_support

from src.shared.config import get_device, settings
from src.shared.corruptions import TYPES
from src.shared.datasets.corrupted import CorruptedPets
from src.shared.evaluation import SEV_NAME, aggregate, score_test
from src.shared.manifests import load
from src.task1.evaluate import figure, load_model
from src.task2.inference import load_router

DESC = {(1, 0): "false clean bypass", (2, 0): "false clean bypass", (3, 0): "false clean bypass",
        (1, 2): "cross-corruption: salt-pepper -> blur specialist", (1, 3): "salt-pepper -> occlusion specialist",
        (2, 3): "blur -> occlusion specialist (hallucinated patches)", (2, 1): "blur -> salt-pepper specialist",
        (3, 1): "occlusion -> salt-pepper specialist", (3, 2): "occlusion -> blur specialist",
        (0, 1): "clean over-processed by salt specialist", (0, 2): "clean over-processed by blur specialist",
        (0, 3): "clean over-processed by occlusion specialist"}


class FnModel(nn.Module):
    def __init__(self, fn):
        super().__init__()
        self.fn = fn

    def forward(self, x):
        return self.fn(x)


if __name__ == "__main__":
    dev = get_device()
    router = load_router(dev)
    t1, _ = load_model(settings.checkpoint_dir / "task1" / "best_model.pth", dev)
    preds = []

    def predicted(xc, lab):
        o = router(xc)
        preds.append(o["routing_decision"].cpu())
        return o["reconstructed"]

    r_t1 = score_test(lambda xc, lab: t1(xc))
    r_or = score_test(lambda xc, lab: router(xc, oracle_labels=lab)["reconstructed"])
    r_pr = score_test(predicted)
    pred = torch.cat(preds).numpy()
    y = r_pr["label"]
    pr, rc, f1, _ = precision_recall_fscore_support(y, pred, labels=range(4), zero_division=0)
    cm = confusion_matrix(y, pred, labels=range(4)).astype(float)
    cls = {"accuracy": float((y == pred).mean()), "macro_precision": float(pr.mean()), "macro_recall": float(rc.mean()),
           "macro_f1": float(f1.mean()), "per_class": {TYPES[i]: {"precision": float(pr[i]), "recall": float(rc[i]),
                                                                  "f1": float(f1[i])} for i in range(4)},
           "confusion_counts": cm.astype(int).tolist(), "confusion_normalized": (cm / cm.sum(1, keepdims=True)).tolist()}
    a1, ao, ap_ = aggregate(r_t1), aggregate(r_or), aggregate(r_pr)
    table = []
    for k in ap_["per_severity"]:
        row = {"condition": k, "params": ap_["per_severity"][k]["params"]}
        for tag, a in (("t1", a1), ("oracle", ao), ("pred", ap_)):
            for m in ("psnr", "ssim", "l1"):
                row[f"{tag}_{m}"] = a["per_severity"][k][m]
        row["gap_psnr"] = row["oracle_psnr"] - row["pred_psnr"]
        row["gap_ssim"] = row["oracle_ssim"] - row["pred_ssim"]
        table.append(row)
    res = {"classifier_test": cls, "task1": a1, "oracle": ao, "predicted": ap_, "table": table,
           "latency_ms_per_sample": {"task1": r_t1["ms_per_sample"], "oracle": r_or["ms_per_sample"],
                                     "predicted": r_pr["ms_per_sample"]}}
    out = settings.results_dir / "task2"
    vis = out / "visuals"
    vis.mkdir(parents=True, exist_ok=True)
    (out / "metrics_summary.json").write_text(json.dumps(res, indent=2))
    with open(out / "metrics_summary.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(table[0]))
        w.writeheader()
        w.writerows(table)
    print("classifier test", {k: round(v, 4) for k, v in cls.items() if not isinstance(v, (dict, list))})
    for row in table:
        print(f"{row['condition']:20s} T1 {row['t1_psnr']:.2f} | oracle {row['oracle_psnr']:.2f} | pred {row['pred_psnr']:.2f} | gap {row['gap_psnr']:.3f}")
    for tag, a in (("task1", a1), ("oracle", ao), ("predicted", ap_)):
        print(tag, "overall", {k: round(v, 4) for k, v in a["overall"].items()}, "corrupted-only", {k: round(v, 4) for k, v in a["overall_corrupted"].items()}, {k: round(v["psnr"], 2) for k, v in a["per_corruption"].items()})
    print("latency ms/sample", res["latency_ms_per_sample"])

    ds = CorruptedPets("test")
    man = load("test_manifest.json")
    rng = random.Random(0)
    idxs, titles = [], []
    for ci, t in enumerate(TYPES):
        for j in range(3):
            sev = 0 if ci == 0 else j + 1
            cand = np.where((r_pr["label"] == ci) & (r_pr["sev"] == sev))[0]
            idxs.append(int(rng.choice(list(cand))))
            titles.append(f"{t}\n{SEV_NAME[sev]}")
    for g in range(0, 12, 3):
        figure(FnModel(lambda x: router(x)["reconstructed"]), ds, idxs[g:g + 3], titles[g:g + 3],
               vis / f"examples_{TYPES[g // 3]}.png", dev)
    # misrouting audit: the largest-PSNR-drop sample for each distinct (true, predicted) pair
    drop = r_or["psnr"] - r_pr["psnr"]
    best = {}
    for i in np.where(pred != y)[0]:
        k = (int(y[i]), int(pred[i]))
        if k not in best or drop[i] > drop[best[k]]:
            best[k] = int(i)
    n_pairs = {k: int(((y == k[0]) & (pred == k[1])).sum()) for k in best}
    ranked = sorted(best.items(), key=lambda kv: -drop[kv[1]])[:4]
    fails = []
    for n, ((tl, pl), i) in enumerate(ranked):
        figure(FnModel(lambda x: router(x)["reconstructed"]), ds, [i],
               [f"true {TYPES[tl]} -> routed {TYPES[pl]}\nPSNR {r_pr['psnr'][i]:.1f} (oracle {r_or['psnr'][i]:.1f})"],
               vis / f"misroute_{n + 1}.png", dev)
        fails.append({"manifest_idx": i, "image_idx": man[i]["idx"], "true": TYPES[tl], "routed_to": TYPES[pl],
                      "severity": man[i]["severity"], "type": DESC.get((tl, pl), "misroute"),
                      "psnr_predicted": float(r_pr["psnr"][i]), "psnr_oracle": float(r_or["psnr"][i]),
                      "n_such_errors_in_test": n_pairs[(tl, pl)]})
    (out / "misrouting_cases.json").write_text(json.dumps({"n_misrouted": int((pred != y).sum()), "n_total": int(len(y)),
                                                           "cases": fails}, indent=2))
    print("misrouted", int((pred != y).sum()), "of", len(y))
    for f in fails:
        print(f)
