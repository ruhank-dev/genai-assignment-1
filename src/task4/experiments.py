"""Step 2 (style conditioning: concat vs FiLM) and Step 3 (PatchGAN receptive field: 16x16 vs 70x70) experiments.
15 epochs each, same seed. Besides val L1/SSIM/PSNR two style metrics are computed on the validation faces:
  distinctness = mean L1 between sketches generated for the same photo under two different styles
  style_gap    = mean L1(G(x, wrong style), GT) - L1(G(x, true style), GT)   (>0: style matters for fidelity)"""
import argparse
import json

import torch
from torch.utils.data import DataLoader

from src.shared.config import get_device, settings
from src.shared.datasets.fs2k import FS2KDataset
from src.task4.generator import UNetGenerator
from src.task4.train import BASELINE, train_gan, unit

OUT = settings.results_dir / "task4"


@torch.no_grad()
def style_metrics(ckpt_path) -> dict:
    dev = get_device()
    ck = torch.load(ckpt_path, map_location=dev)
    c = ck["config"]
    g = UNetGenerator(c["base"], c["emb_dim"], c["dropout"], c["style_mode"]).to(dev)
    g.load_state_dict(ck["model_state_dict"])
    g.eval()
    dist, gap, n = 0.0, 0.0, 0
    for x, y, s in DataLoader(FS2KDataset("val"), 64):
        x, y, s = x.to(dev), y.to(dev), s.to(dev)
        outs = [g(x, torch.full_like(s, k)) for k in range(3)]
        dist += sum((outs[i] - outs[j]).abs().mean().item() for i in range(3) for j in range(i + 1, 3)) / 3 * len(x)
        true = g(x, s)
        wrong = g(x, (s + 1) % 3)
        gap += ((unit(wrong) - unit(y)).abs().mean() - (unit(true) - unit(y)).abs().mean()).item() * len(x)
        n += len(x)
    return {"distinctness": dist / n, "style_gap": gap / n}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("which", choices=["style", "disc"])
    ap.add_argument("--epochs", type=int, default=15)
    a = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    variants = ({"concat": {"style_mode": "concat"}, "film": {"style_mode": "film"}} if a.which == "style"
                else {"patch16": {"d_layers": 1}, "patch70": {"d_layers": 3}})
    rows = []
    for name, over in variants.items():
        d = settings.checkpoint_dir / "task4" / "exp" / name
        r = train_gan({**BASELINE, **over}, a.epochs, d, "", f"genai-task4-{a.which}-experiment", name, grid_every=0)
        h = r["history"]
        i = min(range(len(h["val_l1"])), key=lambda k: h["val_l1"][k])
        rows.append({"variant": name, "best_epoch": i, "val_l1": h["val_l1"][i], "val_psnr": h["val_psnr"][i],
                     "val_ssim": h["val_ssim"][i], "final_d_loss": h["total_d_loss"][-1], "final_g_adv": h["g_adv_loss"][-1],
                     **style_metrics(d / "generator.pth")})
        print(rows[-1], flush=True)
    (OUT / f"{a.which}_experiment.json").write_text(json.dumps(rows, indent=2))
