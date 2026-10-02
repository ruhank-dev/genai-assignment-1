"""Training loop for the universal AE; reused by Task 2 specialists via `types`."""
import argparse
import json
import time
from pathlib import Path

import optuna
import torch
from torch.utils.data import DataLoader

from src.shared.config import get_device, seed_everything, settings
from src.shared.corruptions import TYPES
from src.shared.datasets.corrupted import CorruptedPets
from src.shared.losses import rec_loss
from src.shared.metrics import l1_per_image, psnr_per_image, ssim_per_image
from src.shared.tracking import ExperimentTracker
from src.shared.visualization import make_error_heatmap, make_reconstruction_grid, plot_training_curves
from src.task1.autoencoder import UniversalAutoencoder

BASELINE = dict(lr=1e-3, batch_size=32, bottleneck_dim=128, channels=[32, 64, 128, 256], dropout=0.0, alpha=0.8,
                weight_decay=1e-4)


def loader(ds, bs, shuffle):
    nw = settings.num_workers
    return DataLoader(ds, bs, shuffle=shuffle, num_workers=nw, pin_memory=torch.cuda.is_available(),
                      persistent_workers=nw > 0, drop_last=shuffle)


@torch.no_grad()
def validate(model, dl, device, alpha) -> dict:
    """Aggregate + per-corruption metrics on the deterministic manifest. objective = L1 + (1-SSIM) (alpha-free)."""
    model.eval()
    rows = {"loss": [], "psnr": [], "ssim": [], "l1": [], "label": []}
    for xc, x, lab, _ in dl:
        xc, x = xc.to(device), x.to(device)
        y = model(xc)
        rows["loss"].append(torch.full((len(x),), rec_loss(x, y, alpha).item()))
        rows["psnr"].append(psnr_per_image(x, y).cpu())
        rows["ssim"].append(ssim_per_image(x, y).cpu())
        rows["l1"].append(l1_per_image(x, y).cpu())
        rows["label"].append(lab)
    r = {k: torch.cat(v) for k, v in rows.items()}
    out = {k: r[k].mean().item() for k in ("loss", "psnr", "ssim", "l1")}
    out["objective"] = out["l1"] + 1 - out["ssim"]
    for ci, t in enumerate(TYPES):
        m = r["label"] == ci
        if m.any():
            out.update({f"{t}_psnr": r["psnr"][m].mean().item(), f"{t}_ssim": r["ssim"][m].mean().item()})
    return out


def train_model(cfg: dict, epochs: int, ckpt_dir: Path, ckpt_name: str, experiment: str, run_name: str,
                types: list[str] | None = None, trial: optuna.Trial | None = None, patience: int = 10,
                train_fraction: float = 1.0, log_images: bool = True, tags: dict | None = None) -> dict:
    seed_everything()
    dev = get_device()
    tr_ds = CorruptedPets("train", types=types)
    if train_fraction < 1:
        tr_ds.base.paths = tr_ds.base.paths[: int(len(tr_ds.base) * train_fraction)]
        tr_ds.base.labels = tr_ds.base.labels[: len(tr_ds.base.paths)]
    tr, va = loader(tr_ds, cfg["batch_size"], True), loader(CorruptedPets("val", types=types), 64, False)
    model = UniversalAutoencoder(cfg["channels"], cfg["bottleneck_dim"], cfg["dropout"]).to(dev)
    opt = torch.optim.AdamW(model.parameters(), lr=cfg["lr"], weight_decay=cfg.get("weight_decay", 1e-4))
    sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, epochs)
    scaler = torch.amp.GradScaler(enabled=dev.type == "cuda")
    tracker = ExperimentTracker()
    tracker.start_run(run_name, experiment, tags=tags, nested=trial is not None)
    tracker.log_params({**cfg, "epochs": epochs, "types": types or "all", "n_params": model.n_params,
                        "compression_ratio": round(model.compression_ratio(), 2), "seed": settings.seed,
                        "amp": dev.type == "cuda"})
    ckpt_dir.mkdir(parents=True, exist_ok=True)
    hist, best, bad = {}, float("inf"), 0
    fixed = next(iter(va))  # fixed validation batch for visual progress
    try:
        for ep in range(epochs):
            model.train()
            t0, tl = time.time(), 0.0
            for xc, x, _, _ in tr:
                xc, x = xc.to(dev, non_blocking=True), x.to(dev, non_blocking=True)
                with torch.autocast(dev.type, enabled=dev.type == "cuda"):
                    y = model(xc)
                loss = rec_loss(x, y.float(), cfg["alpha"])
                opt.zero_grad(set_to_none=True)
                scaler.scale(loss).backward()
                scaler.step(opt)
                scaler.update()
                tl += loss.item()
            sched.step()
            v = validate(model, va, dev, cfg["alpha"])
            tl /= len(tr)
            for k, val in {"train_loss": tl, "val_loss": v["loss"], "val_psnr": v["psnr"], "val_ssim": v["ssim"],
                           "val_l1": v["l1"], "val_objective": v["objective"]}.items():
                hist.setdefault(k, []).append(val)
            tracker.log_metrics({"train_loss": tl, **{f"val_{k}": x for k, x in v.items()}}, step=ep)
            print(f"[{run_name}] ep{ep} train {tl:.4f} val {v['loss']:.4f} psnr {v['psnr']:.2f} ssim {v['ssim']:.4f} "
                  f"({time.time() - t0:.0f}s)", flush=True)
            if log_images and ep % 5 == 0:
                with torch.no_grad():
                    xc, x = fixed[0].to(dev), fixed[1].to(dev)
                    y = model.eval()(xc)
                tracker.log_image("recon_grid", make_reconstruction_grid(xc, y, x), ep)
            if v["objective"] < best:
                best, bad = v["objective"], 0
                torch.save({"model_state_dict": model.state_dict(), "optimizer_state_dict": opt.state_dict(),
                            "epoch": ep, "best_val_objective": best, "val_metrics": v, "config": cfg},
                           ckpt_dir / ckpt_name)
            else:
                bad += 1
            if trial is not None:
                trial.report(v["objective"], ep)
                if trial.should_prune():
                    raise optuna.TrialPruned()
            if bad >= patience:
                break
        fig = plot_training_curves(hist)
        tracker.log_figure("curves", fig, epochs)
    finally:
        tracker.end_run()
    return {"best_val_objective": best, "history": hist}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["baseline", "final"], default="baseline")
    ap.add_argument("--epochs", type=int, default=30)
    ap.add_argument("--smoke", action="store_true")
    a = ap.parse_args()
    out = settings.results_dir / "task1"
    out.mkdir(parents=True, exist_ok=True)
    if a.mode == "final":
        cfg = json.loads((out / "best_hyperparams.json").read_text())["config"]
        name, run = "best_model.pth", "final"
    else:
        cfg, name, run = BASELINE, "baseline_best.pth", "baseline"
    res = train_model(cfg, 1 if a.smoke else a.epochs, settings.checkpoint_dir / "task1", name,
                      "genai-task1-universal-ae", run, train_fraction=0.1 if a.smoke else 1.0)
    (out / f"{run}_history.json").write_text(json.dumps(res))
