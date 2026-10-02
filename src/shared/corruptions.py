"""Corruptions as pure functions of (image, params). Params are JSON-able primitives so that
manifests can persist them; stochastic ones are re-seeded from params['seed'] for determinism."""
import math
import random
from typing import Optional

import torch
from torchvision.transforms.functional import gaussian_blur

TYPES = ["clean", "salt_pepper", "blur", "occlusion"]  # class ids 0..3
SP_LEVELS = [0.03, 0.08, 0.15]
BLUR_LEVELS = [(3, 0.7), (5, 1.5), (7, 2.5)]
OCC_LEVELS = [(1, 0.10), (2, 0.20), (3, 0.35)]  # (n_rects, total area fraction)
H = W = 128


def make_boxes(n: int, area_frac: float, rng: random.Random, equal: bool = False) -> list[list[int]]:
    """n rectangles [y1,x1,y2,x2] whose areas sum to ~area_frac*H*W (overlap may reduce coverage slightly)."""
    total = area_frac * H * W
    w = [1.0] * n if equal else [rng.uniform(0.5, 1.5) for _ in range(n)]
    boxes, taken = [], torch.zeros(H, W, dtype=torch.bool)
    for wi in w:
        a = total * wi / sum(w)
        ar = rng.uniform(0.6, 1.6)
        h = max(2, min(H, int(round(math.sqrt(a * ar)))))
        wd = max(2, min(W, int(round(a / h))))
        # best of 40 random placements = least overlap with earlier boxes (keeps total coverage ~ target)
        cands = [(rng.randint(0, H - h), rng.randint(0, W - wd)) for _ in range(40)]
        y1, x1 = min(cands, key=lambda c: int(taken[c[0]:c[0] + h, c[1]:c[1] + wd].sum()))
        taken[y1:y1 + h, x1:x1 + wd] = True
        boxes.append([y1, x1, y1 + h, x1 + wd])
    return boxes


def sample_params(ctype: str, rng: random.Random, level: Optional[int] = None) -> dict:
    """level=None -> training distribution; level in 1..3 -> fixed test severity."""
    p: dict = {"type": ctype, "severity": level or 0, "seed": rng.randrange(2**31)}
    if ctype == "salt_pepper":
        p["p"] = SP_LEVELS[level - 1] if level else rng.uniform(0.02, 0.15)
    elif ctype == "blur":
        p["k"], p["sigma"] = BLUR_LEVELS[level - 1] if level else (rng.choice([3, 5, 7]), rng.uniform(0.5, 2.5))
    elif ctype == "occlusion":
        n, frac = OCC_LEVELS[level - 1] if level else (rng.randint(1, 3), rng.uniform(0.10, 0.35))
        p["boxes"] = make_boxes(n, frac, rng, equal=level is not None)
    return p


def apply_corruption(x: torch.Tensor, p: dict) -> torch.Tensor:
    """x: (3,H,W) in [0,1]. Returns corrupted copy."""
    t = p["type"]
    if t == "clean":
        return x
    if t == "salt_pepper":
        g = torch.Generator().manual_seed(p["seed"])
        u = torch.rand(x.shape[-2:], generator=g)  # pixel-level (same across channels)
        s = torch.rand(x.shape[-2:], generator=g) < 0.5
        y = x.clone()
        hit = u < p["p"]
        y[:, hit & s] = 1.0
        y[:, hit & ~s] = 0.0
        return y
    if t == "blur":
        return gaussian_blur(x, [p["k"], p["k"]], [p["sigma"], p["sigma"]])
    if t == "occlusion":
        y = x.clone()
        for y1, x1, y2, x2 in p["boxes"]:
            y[:, y1:y2, x1:x2] = 0.0
        return y
    raise ValueError(t)


def occlusion_coverage(p: dict) -> float:
    m = torch.zeros(H, W, dtype=torch.bool)
    for y1, x1, y2, x2 in p["boxes"]:
        m[y1:y2, x1:x2] = True
    return m.float().mean().item()
