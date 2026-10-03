"""Task 3 two-phase training: gate warm-up (experts frozen) -> joint fine-tune (experts unfrozen, lower LR)."""
import argparse
import json
import time

import optuna
import torch
import torch.nn.functional as F
from torch.utils.data import DataLoader

from src.shared.config import get_device, seed_everything, settings
from src.shared.corruptions import TYPES
from src.shared.datasets.corrupted import BalancedBatchSampler, CorruptedPets
from src.shared.losses import l1_loss, ssim_loss
from src.shared.metrics import l1_per_image, psnr_per_image, ssim_per_image
from src.shared.tracking import ExperimentTracker
from src.task2.inference import load_classifier, load_specialist
from src.task2.specialist import SPEC_FILES, SPEC_TYPES
from src.task3.balance import BALANCE
from src.task3.gate import GatingNetwork
from src.task3.moe_model import SoftMoE

BASELINE = dict(tau=1.0, alpha=0.8, lam_ce=0.1, lam_bal=0.01, fine_tune_lr=2e-5, warmup_lr=1e-3, batch_size=32,
                balance="l2", head_type="linear")


def build_moe(dev, head_type: str = "linear") -> SoftMoE:
    """Initialise from Task 2: gate <- classifier, experts <- trained specialists."""
    d = settings.checkpoint_dir / "task2"
    gate = GatingNetwork(load_classifier(d / "classifier_best.pt", dev), head_type)
    ex = [load_specialist(d / SPEC_FILES[t], dev) for t in SPEC_TYPES]
    return SoftMoE(gate, *ex).to(dev)


def set_experts_frozen(model: SoftMoE, frozen: bool) -> None:
    for p in model.experts.parameters():
        p.requires_grad_(not frozen)


def moe_loss(out, w, z, x, labels, cfg) -> tuple[torch.Tensor, dict]:
    """L = a*L1 + (1-a)*(1-SSIM) + lam_ce*CE(z, y) + lam_bal*balance(w); lambda1=a, lambda2=1-a."""
    l1, ss = l1_loss(x, out), ssim_loss(x, out)
    ce, bal = F.cross_entropy(z, labels), BALANCE[cfg["balance"]](w)
    loss = cfg["alpha"] * l1 + (1 - cfg["alpha"]) * ss + cfg["lam_ce"] * ce + cfg["lam_bal"] * bal
    return loss, {"l1": l1.item(), "ssim_loss": ss.item(), "ce": ce.item(), "balance": bal.item()}


@torch.no_grad()
def validate(model, dl, dev, cfg) -> dict:
    model.eval()
    acc = {k: [] for k in ("psnr", "ssim", "l1", "label")}
    ws, ce_sum, n = [], 0.0, 0
    for xc, x, lab, _ in dl:
        xc, x, lab = xc.to(dev), x.to(dev), lab.to(dev)
        out, w, z = model(xc, cfg["tau"])
        acc["psnr"].append(psnr_per_image(x, out).cpu())
        acc["ssim"].append(ssim_per_image(x, out).cpu())
        acc["l1"].append(l1_per_image(x, out).cpu())
        acc["label"].append(lab.cpu())
        ws.append(w.cpu())
        ce_sum += F.cross_entropy(z, lab, reduction="sum").item()
        n += len(x)
    r = {k: torch.cat(v) for k, v in acc.items()}
    w = torch.cat(ws)
    m = {"psnr": r["psnr"].mean().item(), "ssim": r["ssim"].mean().item(), "l1": r["l1"].mean().item(),
         "ce": ce_sum / n, "gate_acc": (w.argmax(1) == r["label"]).float().mean().item(),
         "w_mean": w.mean(0).tolist()}
    m["psnr_corrupted"] = r["psnr"][r["label"] != 0].mean().item()  # clean is an exact bypass (80 dB cap): report apart
    m["objective_loss"] = cfg["alpha"] * m["l1"] + (1 - cfg["alpha"]) * (1 - m["ssim"])
    for ci, t in enumerate(TYPES):
        m[f"w_{t}"] = w[r["label"] == ci].mean(0).tolist()
    return m


def collapsed(w_mean: list[float]) -> bool:
    return max(w_mean) > 0.90 or min(w_mean) < 0.02


def run_training(cfg: dict, warmup_epochs: int, joint_epochs: int, ckpt_dir, ckpt_name: str, experiment: str,
                 run_name: str, trial: optuna.Trial | None = None, tags: dict | None = None,
                 collapse_prune: bool = False, log_images: bool = False) -> dict:
    seed_everything()
    dev = get_device()
    ds = CorruptedPets("train", balanced=True)
    n_img = len(ds) // 4
    bs = cfg["batch_size"]
    sampler = BalancedBatchSampler(n_img, bs, settings.seed, epoch_batches=n_img // bs)  # epoch ~ n_img samples
    tr = DataLoader(ds, batch_sampler=sampler, num_workers=settings.num_workers, pin_memory=True, persistent_workers=True)
    va = DataLoader(CorruptedPets("val"), 128, num_workers=settings.num_workers)
    model = build_moe(dev, cfg.get("head_type", "linear"))
    tracker = ExperimentTracker()
    tracker.start_run(run_name, experiment, tags=tags, nested=trial is not None)
    tracker.log_params({**cfg, "warmup_epochs": warmup_epochs, "joint_epochs": joint_epochs, "seed": settings.seed})
    hist: dict = {}
    best, ep_global = -1.0, 0
    ckpt_dir.mkdir(parents=True, exist_ok=True)
    try:
        for phase, n_ep in (("warmup", warmup_epochs), ("joint", joint_epochs)):
            if n_ep == 0:
                continue
            set_experts_frozen(model, phase == "warmup")
            if phase == "warmup":
                groups = [{"params": model.gate.parameters(), "lr": cfg["warmup_lr"]}]
            else:  # differential LRs: experts fine_tune_lr, gate 5x (plan ratio 2e-5 : 1e-4)
                groups = [{"params": model.gate.parameters(), "lr": 5 * cfg["fine_tune_lr"]},
                          {"params": model.experts.parameters(), "lr": cfg["fine_tune_lr"]}]
            opt = torch.optim.Adam(groups)
            sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, n_ep)
            for ep in range(n_ep):
                model.train()
                if phase == "warmup" or cfg.get("freeze_expert_bn", True):
                    # warm-up: experts fully frozen. joint: weights train but BatchNorm running stats stay those of
                    # the specialist training (every expert sees ALL corruption types in the MoE forward, which would
                    # otherwise drift its BN statistics - observed val SSIM decline in the first joint runs).
                    model.experts.eval()
                t0, tl = time.time(), 0.0
                for xc, x, lab, _ in tr:
                    xc, x, lab = xc.to(dev, non_blocking=True), x.to(dev, non_blocking=True), lab.to(dev)
                    out, w, z = model(xc, cfg["tau"])
                    loss, parts = moe_loss(out, w, z, x, lab, cfg)
                    opt.zero_grad(set_to_none=True)
                    loss.backward()
                    opt.step()
                    tl += loss.item()
                sched.step()
                v = validate(model, va, dev, cfg)
                tl /= len(tr)
                for k, val in (("train_loss", tl), ("val_psnr", v["psnr"]), ("val_ssim", v["ssim"]), ("val_l1", v["l1"]),
                               ("val_ce", v["ce"]), ("val_gate_acc", v["gate_acc"]), ("val_loss", v["objective_loss"])):
                    hist.setdefault(k, []).append(val)
                hist.setdefault("w_mean", []).append(v["w_mean"])
                tracker.log_metrics({"train_loss": tl, "val_psnr": v["psnr"], "val_ssim": v["ssim"], "val_l1": v["l1"],
                                     "val_ce": v["ce"], "val_gate_acc": v["gate_acc"],
                                     **{f"w_mean_{i}": x for i, x in enumerate(v["w_mean"])}}, ep_global)
                alert = " COLLAPSE?" if collapsed(v["w_mean"]) else ""
                print(f"[{run_name}] {phase} ep{ep} train {tl:.4f} psnr {v['psnr']:.2f} psnr_cor {v['psnr_corrupted']:.2f} ssim {v['ssim']:.4f} "
                      f"gate_acc {v['gate_acc']:.3f} w_mean {[round(a, 3) for a in v['w_mean']]}{alert} "
                      f"({time.time() - t0:.0f}s)", flush=True)
                if v["ssim"] > best:
                    best = v["ssim"]
                    torch.save({"model_state_dict": model.state_dict(), "optimizer_state_dict": opt.state_dict(),
                                "epoch": ep_global, "phase": phase, "best_val_ssim": best, "val_metrics": v,
                                "config": cfg}, ckpt_dir / ckpt_name)
                torch.save({"model_state_dict": model.state_dict(), "optimizer_state_dict": opt.state_dict(),
                            "epoch": ep_global, "config": cfg, "history": hist}, ckpt_dir / "latest.pth")
                if trial is not None:
                    trial.report(v["ssim"], ep_global)
                    if collapse_prune and phase == "joint" and collapsed(v["w_mean"]):
                        raise optuna.TrialPruned("routing collapse: expert dominance > 90% or starvation < 2%")
                    if trial.should_prune():
                        raise optuna.TrialPruned()
                ep_global += 1
    finally:
        tracker.end_run()
    return {"best_val_ssim": best, "history": hist}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["baseline", "final"], default="baseline")
    ap.add_argument("--warmup", type=int, default=5)
    ap.add_argument("--joint", type=int, default=20)
    a = ap.parse_args()
    out = settings.results_dir / "task3"
    out.mkdir(parents=True, exist_ok=True)
    if a.mode == "final":
        cfg = json.loads((out / "best_params.json").read_text())["config"]
        name, run = "best_model.pth", "final"
    else:
        cfg, name, run = BASELINE, "baseline_best.pth", "baseline"
    r = run_training(cfg, a.warmup, a.joint, settings.checkpoint_dir / "task3", name, "genai-task3-soft-moe", run,
                     log_images=True)
    (out / ("baseline_training_log.json" if a.mode == "baseline" else "final_history.json")).write_text(json.dumps(r))
    print("best val ssim", r["best_val_ssim"])
