"""Shared test-manifest evaluation: any callable (xc, label)->restored is scored per sample."""
import time
from typing import Callable

import numpy as np
import torch
from torch.utils.data import DataLoader

from src.shared.config import get_device
from src.shared.corruptions import BLUR_LEVELS, OCC_LEVELS, SP_LEVELS, TYPES
from src.shared.datasets.corrupted import CorruptedPets
from src.shared.metrics import l1_per_image, psnr_per_image, ssim_per_image

SEV_NAME = {0: "-", 1: "low", 2: "medium", 3: "high"}
SEV_PARAM = {"clean": {0: "-"}, "salt_pepper": {i + 1: f"p={p}" for i, p in enumerate(SP_LEVELS)},
             "blur": {i + 1: f"k={k},sigma={s}" for i, (k, s) in enumerate(BLUR_LEVELS)},
             "occlusion": {i + 1: f"{n} rect, ~{int(f * 100)}%" for i, (n, f) in enumerate(OCC_LEVELS)}}


@torch.no_grad()
def score_test(fn: Callable, split: str = "test", bs: int = 128, limit: int | None = None) -> dict:
    """fn(xc, label) -> restored (all on the active device). Returns per-sample numpy arrays + ms/sample."""
    dev = get_device()
    ds = CorruptedPets(split)
    if limit:
        ds.manifest = ds.manifest[:limit]
    dl = DataLoader(ds, bs, num_workers=2, shuffle=False)
    rec = {k: [] for k in ("psnr", "ssim", "l1", "label", "sev")}
    t_total, n = 0.0, 0
    for xc, x, lab, sev in dl:
        xc, x = xc.to(dev), x.to(dev)
        if dev.type == "cuda":
            torch.cuda.synchronize()
        t0 = time.perf_counter()
        y = fn(xc, lab.to(dev))
        if dev.type == "cuda":
            torch.cuda.synchronize()
        t_total += time.perf_counter() - t0
        n += len(x)
        for k, v in (("psnr", psnr_per_image(x, y)), ("ssim", ssim_per_image(x, y)), ("l1", l1_per_image(x, y))):
            rec[k].append(v.cpu())
        rec["label"].append(lab)
        rec["sev"].append(sev)
    out = {k: torch.cat(v).numpy() for k, v in rec.items()}
    out["ms_per_sample"] = 1000 * t_total / n
    return out


def aggregate(r: dict) -> dict:
    """Per-corruption and per-severity tables (+overall mean over all 10 variants per image)."""

    def m(mask):
        return {k: float(r[k][mask].mean()) for k in ("psnr", "ssim", "l1")} | {"n": int(mask.sum())}

    per_c = {t: m(r["label"] == i) for i, t in enumerate(TYPES)}
    per_s = {}
    for i, t in enumerate(TYPES):
        for s in ((0,) if i == 0 else (1, 2, 3)):
            per_s[f"{t}/{SEV_NAME[s]}"] = {"params": SEV_PARAM[t][s], **m((r["label"] == i) & (r["sev"] == s))}
    return {"per_corruption": per_c, "per_severity": per_s, "overall": m(np.ones(len(r["psnr"]), bool)),
            "ms_per_sample": r["ms_per_sample"]}
