"""Classifier training with exactly balanced batches (B/4 per class), CE loss, macro-F1 model selection."""
import argparse
import json
import time

import optuna
import torch
import torch.nn.functional as F
from sklearn.metrics import confusion_matrix, precision_recall_fscore_support
from torch.utils.data import DataLoader

from src.shared.config import get_device, seed_everything, settings
from src.shared.datasets.corrupted import BalancedBatchSampler, CorruptedPets
from src.shared.tracking import ExperimentTracker
from src.task2.classifier import CHANNELS, CLS_NAMES, CorruptionClassifier

def build_classifier(cfg: dict) -> torch.nn.Module:
    """cfg['arch']=='resnet18' only for the architecture comparison experiment (Alternative 3)."""
    if cfg.get("arch") == "resnet18":
        from torchvision.models import ResNet18_Weights, resnet18
        m = resnet18(weights=ResNet18_Weights.IMAGENET1K_V1)
        m.fc = torch.nn.Linear(512, 4)
        return m
    return CorruptionClassifier(CHANNELS[cfg["channel_config"]], cfg["dropout"])


BASELINE = dict(lr=1e-3, batch_size=32, channel_config="medium", dropout=0.2, weight_decay=1e-4)


@torch.no_grad()
def evaluate_cls(model, dl, dev) -> dict:
    model.eval()
    ys, ps = [], []
    for xc, _, lab, _ in dl:
        ps.append(model(xc.to(dev)).argmax(1).cpu())
        ys.append(lab)
    y, p = torch.cat(ys).numpy(), torch.cat(ps).numpy()
    pr, rc, f1, _ = precision_recall_fscore_support(y, p, labels=range(4), zero_division=0)
    cm = confusion_matrix(y, p, labels=range(4)).astype(float)
    per = {n: {"precision": float(pr[i]), "recall": float(rc[i]), "f1": float(f1[i])} for i, n in enumerate(CLS_NAMES)}
    return {"accuracy": float((y == p).mean()), "macro_precision": float(pr.mean()), "macro_recall": float(rc.mean()),
            "macro_f1": float(f1.mean()), "per_class": per,
            "confusion_normalized": (cm / cm.sum(1, keepdims=True)).tolist()}


def train_classifier(cfg: dict, epochs: int, ckpt_path, experiment: str, run_name: str,
                     trial: optuna.Trial | None = None, tags: dict | None = None) -> dict:
    seed_everything()
    dev = get_device()
    ds = CorruptedPets("train", balanced=True)
    n_img, nw = len(ds) // 4, settings.num_workers
    tr = DataLoader(ds, batch_sampler=BalancedBatchSampler(n_img, cfg["batch_size"], settings.seed),
                    num_workers=nw, pin_memory=True, persistent_workers=True)
    va = DataLoader(CorruptedPets("val"), 128, num_workers=nw)
    model = build_classifier(cfg).to(dev)
    opt = torch.optim.AdamW(model.parameters(), lr=cfg["lr"], weight_decay=cfg["weight_decay"])
    sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, epochs)
    tracker = ExperimentTracker()
    tracker.start_run(run_name, experiment, tags=tags, nested=trial is not None)
    tracker.log_params({**cfg, "epochs": epochs, "n_params": sum(p.numel() for p in model.parameters()),
                        "seed": settings.seed})
    best, best_m = -1.0, None
    try:
        for ep in range(epochs):
            model.train()
            t0, tl = time.time(), 0.0
            for xc, _, lab, _ in tr:
                loss = F.cross_entropy(model(xc.to(dev, non_blocking=True)), lab.to(dev))
                opt.zero_grad(set_to_none=True)
                loss.backward()
                opt.step()
                tl += loss.item()
            sched.step()
            m = evaluate_cls(model, va, dev)
            tl /= len(tr)
            tracker.log_metrics({"train_loss": tl, "val_acc": m["accuracy"], "val_macro_f1": m["macro_f1"]}, ep)
            print(f"[{run_name}] ep{ep} loss {tl:.4f} acc {m['accuracy']:.4f} f1 {m['macro_f1']:.4f} "
                  f"({time.time() - t0:.0f}s)", flush=True)
            if m["macro_f1"] > best:
                best, best_m = m["macro_f1"], m
                ckpt_path.parent.mkdir(parents=True, exist_ok=True)
                torch.save({"model_state_dict": model.state_dict(), "optimizer_state_dict": opt.state_dict(),
                            "epoch": ep, "best_macro_f1": best, "val_metrics": m, "config": cfg}, ckpt_path)
            if trial is not None:
                trial.report(m["macro_f1"], ep)
                if trial.should_prune():
                    raise optuna.TrialPruned()
    finally:
        tracker.end_run()
    return {"best_macro_f1": best, "metrics": best_m}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["baseline", "final"], default="baseline")
    ap.add_argument("--epochs", type=int, default=20)
    a = ap.parse_args()
    out = settings.results_dir / "task2"
    out.mkdir(parents=True, exist_ok=True)
    cfg = json.loads((out / "classifier_best_params.json").read_text())["config"] if a.mode == "final" else BASELINE
    name = "classifier_best.pt" if a.mode == "final" else "classifier_baseline.pt"
    r = train_classifier(cfg, a.epochs, settings.checkpoint_dir / "task2" / name, "genai-task2-classifier", a.mode)
    (out / f"classifier_{a.mode}_metrics.json").write_text(json.dumps(r["metrics"], indent=2))
    print(json.dumps({k: v for k, v in r["metrics"].items() if k != "per_class"}))
