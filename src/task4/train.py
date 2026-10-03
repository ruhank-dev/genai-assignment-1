"""Conditional GAN training: alternating D / G updates, decoupled loss logging, fixed-sample grids."""
import argparse
import json
import math
import time

import optuna
import torch
import torch.nn.functional as F
from torch.utils.data import DataLoader

from src.shared.config import get_device, seed_everything, settings
from src.shared.datasets.fs2k import FS2KDataset
from src.shared.metrics import l1_per_image, psnr_per_image, ssim_per_image
from src.shared.tracking import ExperimentTracker
from src.shared.visualization import plot_training_curves
from src.task4.augmentation import PairedAugment
from src.task4.discriminator import PatchDiscriminator
from src.task4.generator import UNetGenerator

BASELINE = dict(g_lr=2e-4, d_lr=2e-4, batch_size=8, base=64, dropout=0.3, emb_dim=16, lambda_l1=100.0,
                style_mode="film", d_layers=1, label_smooth=0.9)  # d_layers=1: 16x16 PatchGAN won the disc experiment


def unit(x: torch.Tensor) -> torch.Tensor:
    return (x.clamp(-1, 1) + 1) / 2  # [-1,1] -> [0,1] for metrics / images


def build(cfg: dict, dev):
    g = UNetGenerator(cfg["base"], cfg["emb_dim"], cfg["dropout"], cfg["style_mode"]).to(dev)
    d = PatchDiscriminator(cfg["base"], cfg["emb_dim"], cfg["d_layers"]).to(dev)
    return g, d


@torch.no_grad()
def validate(g, dl, dev) -> dict:
    g.eval()
    acc = {"l1": [], "psnr": [], "ssim": [], "style": []}
    for x, y, s in dl:
        x, y, s = x.to(dev), y.to(dev), s.to(dev)
        fake = g(x, s)
        a, b = unit(y), unit(fake)
        acc["l1"].append(l1_per_image(a, b).cpu())
        acc["psnr"].append(psnr_per_image(a, b).cpu())
        acc["ssim"].append(ssim_per_image(a, b).cpu())
        acc["style"].append(s.cpu())
    r = {k: torch.cat(v) for k, v in acc.items()}
    out = {k: r[k].mean().item() for k in ("l1", "psnr", "ssim")}
    for st in range(3):
        m = r["style"] == st
        if m.any():
            out.update({f"style{st + 1}_{k}": r[k][m].mean().item() for k in ("l1", "psnr", "ssim")})
    return out


def fixed_grid(g, ds, idx, dev) -> torch.Tensor:
    """Rows = fixed validation faces (2 per style): [photo | ground-truth sketch | generated sketch]."""
    x = torch.stack([ds[i][0] for i in idx]).to(dev)
    y = torch.stack([ds[i][1] for i in idx])
    s = torch.tensor([ds.styles[i] for i in idx], device=dev)
    g.eval()
    with torch.no_grad():
        fake = g(x, s).cpu()
    rows = [torch.cat([unit(x[i].cpu()), unit(y[i]), unit(fake[i])], dim=2) for i in range(len(idx))]
    return torch.cat(rows, dim=1)


def fixed_indices(ds) -> list[int]:
    idx = []
    for st in range(3):
        idx += [i for i, s in enumerate(ds.styles) if s == st][:2]
    return idx


def train_gan(cfg: dict, epochs: int, ckpt_dir, prefix: str, experiment: str, run_name: str,
              trial: optuna.Trial | None = None, grid_every: int = 5, tags: dict | None = None) -> dict:
    seed_everything()
    dev = get_device()
    tr_ds, va_ds = FS2KDataset("train", transform=PairedAugment(seed=settings.seed)), FS2KDataset("val")
    tr = DataLoader(tr_ds, cfg["batch_size"], shuffle=True, drop_last=True, num_workers=0)
    va = DataLoader(va_ds, 64, num_workers=0)
    g, d = build(cfg, dev)
    og = torch.optim.Adam(g.parameters(), cfg["g_lr"], betas=(0.5, 0.999))
    od = torch.optim.Adam(d.parameters(), cfg["d_lr"], betas=(0.5, 0.999))
    half = epochs // 2  # constant LR for the first half, then linear decay to 0
    lam = lambda e: 1.0 if e < half else max(0.0, 1.0 - (e - half) / max(1, epochs - half))
    sg, sd = torch.optim.lr_scheduler.LambdaLR(og, lam), torch.optim.lr_scheduler.LambdaLR(od, lam)
    fidx = fixed_indices(va_ds)
    tracker = ExperimentTracker()
    tracker.start_run(run_name, experiment, tags=tags, nested=trial is not None)
    tracker.log_params({**cfg, "epochs": epochs, "g_params": sum(p.numel() for p in g.parameters()),
                        "d_params": sum(p.numel() for p in d.parameters()), "seed": settings.seed})
    ckpt_dir.mkdir(parents=True, exist_ok=True)
    hist: dict = {}
    best = float("inf")
    try:
        for ep in range(epochs):
            g.train()
            d.train()
            t0 = time.time()
            sums = {"d_real_loss": 0.0, "d_fake_loss": 0.0, "g_adv_loss": 0.0, "g_l1_loss": 0.0}
            for x, y, s in tr:
                x, y, s = x.to(dev), y.to(dev), s.to(dev)
                fake = g(x, s)
                # --- D step: real pair -> 1 (one-sided smoothing), fake pair -> 0
                pr, pf = d(x, y, s), d(x, fake.detach(), s)
                l_real = F.binary_cross_entropy_with_logits(pr, torch.full_like(pr, cfg["label_smooth"]))
                l_fake = F.binary_cross_entropy_with_logits(pf, torch.zeros_like(pf))
                od.zero_grad(set_to_none=True)
                (0.5 * (l_real + l_fake)).backward()
                od.step()
                # --- G step: fool D + stay close to the paired sketch
                pg = d(x, fake, s)
                l_adv = F.binary_cross_entropy_with_logits(pg, torch.ones_like(pg))
                l_l1 = F.l1_loss(fake, y)
                loss_g = l_adv + cfg["lambda_l1"] * l_l1
                og.zero_grad(set_to_none=True)
                loss_g.backward()
                og.step()
                for k, v in (("d_real_loss", l_real), ("d_fake_loss", l_fake), ("g_adv_loss", l_adv), ("g_l1_loss", l_l1)):
                    sums[k] += v.item()
            sg.step()
            sd.step()
            n = len(tr)
            m = {k: v / n for k, v in sums.items()}
            m["total_d_loss"] = 0.5 * (m["d_real_loss"] + m["d_fake_loss"])
            m["total_g_loss"] = m["g_adv_loss"] + cfg["lambda_l1"] * m["g_l1_loss"]
            if not all(math.isfinite(v) for v in m.values()):
                if trial is not None:
                    raise optuna.TrialPruned("non-finite loss")
                raise RuntimeError(f"non-finite loss at epoch {ep}: {m}")
            v = validate(g, va, dev)
            for k, val in {**m, **{f"val_{k}": x_ for k, x_ in v.items()}}.items():
                hist.setdefault(k, []).append(val)
            tracker.log_metrics({**m, **{f"val_{k}": x_ for k, x_ in v.items()}}, ep)
            print(f"[{run_name}] ep{ep} D {m['total_d_loss']:.3f} (real {m['d_real_loss']:.3f} fake {m['d_fake_loss']:.3f}) "
                  f"G_adv {m['g_adv_loss']:.3f} G_L1 {m['g_l1_loss']:.4f} | val L1 {v['l1']:.4f} PSNR {v['psnr']:.2f} "
                  f"SSIM {v['ssim']:.4f} ({time.time() - t0:.0f}s)", flush=True)
            if grid_every and (ep % grid_every == 0 or ep == epochs - 1):
                tracker.log_image("fixed_val_grid", fixed_grid(g, va_ds, fidx, dev), ep)
            if v["l1"] < best:
                best = v["l1"]
                torch.save({"model_state_dict": g.state_dict(), "epoch": ep, "val_metrics": v, "config": cfg},
                           ckpt_dir / f"{prefix}generator.pth")
                torch.save({"model_state_dict": d.state_dict(), "optimizer_state_dict": od.state_dict(), "epoch": ep,
                            "config": cfg}, ckpt_dir / f"{prefix}discriminator.pth")
            torch.save({"g": g.state_dict(), "d": d.state_dict(), "og": og.state_dict(), "od": od.state_dict(),
                        "epoch": ep, "config": cfg}, ckpt_dir / "latest.pth")
            if trial is not None:
                trial.report(v["l1"], ep)
                if trial.should_prune():
                    raise optuna.TrialPruned()
        tracker.log_figure("curves", plot_training_curves({"train_loss": hist["g_l1_loss"], "val_loss": hist["val_l1"]}), epochs)
    finally:
        tracker.end_run()
    return {"best_val_l1": best, "history": hist}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["baseline", "final"], default="baseline")
    ap.add_argument("--epochs", type=int, default=60)
    a = ap.parse_args()
    out = settings.results_dir / "task4"
    out.mkdir(parents=True, exist_ok=True)
    if a.mode == "final":
        cfg, prefix, run = json.loads((out / "optuna_best_params.json").read_text())["config"], "best_", "genai-task4-final"
    else:
        cfg, prefix, run = BASELINE, "baseline_", "genai-task4-baseline"
    r = train_gan(cfg, a.epochs, settings.checkpoint_dir / "task4", prefix, "genai-task4-cgan", run)
    (out / f"{a.mode}_history.json").write_text(json.dumps(r))
    print("best val L1", r["best_val_l1"])
