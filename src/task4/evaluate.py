"""Task 4 test evaluation: L1 / SSIM / PSNR / LPIPS (+ FID overall), per style, sample / style-comparison / failure figures."""
import json
import random

import lpips
import matplotlib.pyplot as plt
import numpy as np
import torch
from scipy import linalg
from pytorch_fid.inception import InceptionV3
from torch.utils.data import DataLoader

from src.shared.config import get_device, settings
from src.shared.datasets.fs2k import FS2KDataset
from src.shared.metrics import l1_per_image, psnr_per_image, ssim_per_image
from src.task4.export_onnx import load_generator
from src.task4.train import unit

OUT = settings.results_dir / "task4"


@torch.no_grad()
def inception_feats(model, imgs01: torch.Tensor, dev) -> np.ndarray:
    fs = []
    for i in range(0, len(imgs01), 64):
        fs.append(model(imgs01[i:i + 64].to(dev))[0].squeeze(-1).squeeze(-1).cpu())
    return torch.cat(fs).numpy()


def fid(f1: np.ndarray, f2: np.ndarray) -> float:
    """Frechet distance between Gaussians fitted to Inception features (own implementation: pytorch-fid 0.3 calls
    scipy.linalg.sqrtm(disp=...) which the installed scipy no longer accepts)."""
    m1, m2, s1, s2 = f1.mean(0), f2.mean(0), np.cov(f1, rowvar=False), np.cov(f2, rowvar=False)
    covmean = linalg.sqrtm(s1.dot(s2))
    if not np.isfinite(covmean).all():
        off = np.eye(s1.shape[0]) * 1e-6
        covmean = linalg.sqrtm((s1 + off).dot(s2 + off))
    covmean = covmean.real
    return float(((m1 - m2) ** 2).sum() + np.trace(s1) + np.trace(s2) - 2 * np.trace(covmean))


def show(a, im, title):
    a.imshow(unit(im).permute(1, 2, 0))
    a.axis("off")
    a.set_title(title, fontsize=7)


if __name__ == "__main__":
    dev = get_device()
    g = load_generator(settings.checkpoint_dir / "task4" / "best_generator.pth", dev)
    ds = FS2KDataset("test")
    ann = json.loads((settings.data_dir / "fs2k" / "FS2K" / "anno_test.json").read_text())
    lp = lpips.LPIPS(net="alex").to(dev).eval()
    fakes, per = [], {"l1": [], "ssim": [], "psnr": [], "lpips": []}
    with torch.no_grad():
        for x, y, s in DataLoader(ds, 64):
            x, y, s = x.to(dev), y.to(dev), s.to(dev)
            f = g(x, s)
            a, b = unit(y), unit(f)
            per["l1"].append(l1_per_image(a, b).cpu())
            per["ssim"].append(ssim_per_image(a, b).cpu())
            per["psnr"].append(psnr_per_image(a, b).cpu())
            per["lpips"].append(lp(f, y).flatten().cpu())
            fakes.append(f.cpu())
    per = {k: torch.cat(v).numpy() for k, v in per.items()}
    fakes = torch.cat(fakes)
    st = np.array(ds.styles)
    inc = InceptionV3([InceptionV3.BLOCK_INDEX_BY_DIM[2048]]).to(dev).eval()
    f_real = inception_feats(inc, unit(ds.sketches), dev)
    f_fake = inception_feats(inc, unit(fakes), dev)
    res = {"n_test": len(ds), "overall": {k: float(v.mean()) for k, v in per.items()}, "fid_overall": fid(f_real, f_fake),
           "per_style": {}}
    for k in range(3):
        m = st == k
        res["per_style"][f"style{k + 1}"] = {"n": int(m.sum()), **{n: float(v[m].mean()) for n, v in per.items()}}
    res["notes"] = ("FID uses 1046 images for a 2048-d feature covariance (rank-deficient): treat as a relative number; "
                    "per-style FID is not reported because style 2/3 have only 381/46 test images.")
    (OUT / "test_metrics.json").write_text(json.dumps(res, indent=2))
    print(json.dumps(res, indent=1))
    # 1) diverse sample grid: 13 pairs mixing styles, gender, frontal/non-frontal
    rng = random.Random(0)
    pick = []
    for k, n in ((0, 5), (1, 5), (2, 3)):
        pool = [i for i in range(len(ds)) if st[i] == k]
        rng.shuffle(pool)
        pick += pool[:n]
    fig, ax = plt.subplots(len(pick) // 3 + 1, 9, figsize=(16, 1.9 * (len(pick) // 3 + 1)))
    for a in ax.flat:
        a.axis("off")
    for j, i in enumerate(pick):
        r_, c_ = divmod(j, 3)
        meta = f"s{st[i] + 1} {'F' if ann[i]['gender'] else 'M'} {'frontal' if ann[i]['frontal_face'] else 'side'}"
        show(ax[r_, c_ * 3], ds.photos[i], meta)
        show(ax[r_, c_ * 3 + 1], ds.sketches[i], "GT sketch")
        show(ax[r_, c_ * 3 + 2], fakes[i], f"generated L1 {per['l1'][i]:.3f}")
    fig.tight_layout()
    fig.savefig(OUT / "sample_results_grid.png", dpi=150)
    plt.close(fig)
    # 2) style comparison: same photos under style 1/2/3
    sel = [next(i for i in range(len(ds)) if st[i] == k) for k in range(3)] + [pick[1], pick[6]]
    fig, ax = plt.subplots(len(sel), 6, figsize=(11, 2 * len(sel)))
    with torch.no_grad():
        for r_, i in enumerate(sel):
            xs = ds.photos[i][None].to(dev).repeat(3, 1, 1, 1)
            outs = g(xs, torch.arange(3, device=dev)).cpu()
            show(ax[r_, 0], ds.photos[i], "photo")
            show(ax[r_, 1], ds.sketches[i], f"GT (style {st[i] + 1})")
            for k in range(3):
                show(ax[r_, 2 + k], outs[k], f"generated, style {k + 1}")
            ax[r_, 5].axis("off")
            ax[r_, 5].imshow(unit((outs[0] - outs[2]).abs().mean(0, keepdim=True).repeat(3, 1, 1) * 2).permute(1, 2, 0))
            ax[r_, 5].set_title("|style1 - style3|", fontsize=7)
    fig.tight_layout()
    fig.savefig(OUT / "style_comparison_grid.png", dpi=150)
    plt.close(fig)
    # 3) failure cases: worst L1, one per distinct gender/orientation when possible
    order = np.argsort(-per["l1"])
    fails, seen = [], set()
    for i in order:
        key = (int(st[i]), ann[i]["frontal_face"], ann[i]["gender"])
        if key in seen:
            continue
        seen.add(key)
        fails.append(int(i))
        if len(fails) == 4:
            break
    fig, ax = plt.subplots(len(fails), 3, figsize=(6, 2.1 * len(fails)))
    for r_, i in enumerate(fails):
        show(ax[r_, 0], ds.photos[i], f"s{st[i] + 1} {'F' if ann[i]['gender'] else 'M'} {'frontal' if ann[i]['frontal_face'] else 'side'} "
                                       f"hair{ann[i]['hair']} earring{ann[i]['earring']}")
        show(ax[r_, 1], ds.sketches[i], "GT")
        show(ax[r_, 2], fakes[i], f"L1 {per['l1'][i]:.3f} SSIM {per['ssim'][i]:.2f} LPIPS {per['lpips'][i]:.2f}")
    fig.tight_layout()
    fig.savefig(OUT / "failure_cases_analysis.png", dpi=150)
    plt.close(fig)
    (OUT / "failure_cases.json").write_text(json.dumps([{"test_idx": i, "style": int(st[i]) + 1, "l1": float(per["l1"][i]),
                                                          "ssim": float(per["ssim"][i]), "lpips": float(per["lpips"][i]),
                                                          "anno": {k: ann[i][k] for k in ("gender", "hair", "earring", "smile", "frontal_face")}}
                                                         for i in fails], indent=2))
    md = ["# Task 4 test metrics", "", "| split | n | L1 | SSIM | PSNR | LPIPS |", "|---|---|---|---|---|---|",
          f"| overall | {len(ds)} | {res['overall']['l1']:.4f} | {res['overall']['ssim']:.4f} | {res['overall']['psnr']:.2f} | {res['overall']['lpips']:.4f} |"]
    for k, v in res["per_style"].items():
        md.append(f"| {k} | {v['n']} | {v['l1']:.4f} | {v['ssim']:.4f} | {v['psnr']:.2f} | {v['lpips']:.4f} |")
    md += ["", f"FID (overall): {res['fid_overall']:.2f}", "", res["notes"]]
    (OUT / "test_metrics.md").write_text("\n".join(md))
