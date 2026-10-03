"""NumPy re-implementation of the training corruptions (backend has no torch): same parameters as the test manifests."""
import math
import random

import numpy as np

SP_LEVELS = [0.03, 0.08, 0.15]
BLUR_LEVELS = [(3, 0.7), (5, 1.5), (7, 2.5)]
OCC_LEVELS = [(1, 0.10), (2, 0.20), (3, 0.35)]
H = W = 128
KINDS = ("salt_and_pepper", "gaussian_blur", "rectangular_occlusion")


def salt_pepper(x: np.ndarray, p: float, rng: np.random.Generator) -> np.ndarray:
    hit, salt = rng.random(x.shape[1:]) < p, rng.random(x.shape[1:]) < 0.5
    y = x.copy()
    y[:, hit & salt] = 1.0
    y[:, hit & ~salt] = 0.0
    return y


def gaussian_blur(x: np.ndarray, k: int, sigma: float) -> np.ndarray:
    ax = np.arange(k) - (k - 1) / 2
    ker = np.exp(-(ax ** 2) / (2 * sigma ** 2))
    ker /= ker.sum()
    r = k // 2
    p = np.pad(x, ((0, 0), (r, r), (r, r)), mode="reflect")
    h, w = x.shape[1:]
    tmp = sum(ker[i] * p[:, i:i + h, :] for i in range(k))  # vertical pass
    return sum(ker[j] * tmp[:, :, j:j + w] for j in range(k)).astype(np.float32)  # horizontal pass


def occlusion(x: np.ndarray, n: int, frac: float, rng: random.Random) -> np.ndarray:
    total, taken, y = frac * H * W, np.zeros((H, W), bool), x.copy()
    for _ in range(n):
        a, ar = total / n, rng.uniform(0.6, 1.6)
        h = max(2, min(H, int(round(math.sqrt(a * ar)))))
        w = max(2, min(W, int(round(a / h))))
        cands = [(rng.randint(0, H - h), rng.randint(0, W - w)) for _ in range(40)]
        y1, x1 = min(cands, key=lambda c: int(taken[c[0]:c[0] + h, c[1]:c[1] + w].sum()))  # least overlap
        taken[y1:y1 + h, x1:x1 + w] = True
        y[:, y1:y1 + h, x1:x1 + w] = 0.0
    return y


def apply(x: np.ndarray, kind: str, severity: int, seed: int | None = None) -> tuple[np.ndarray, dict]:
    """severity 1..3 -> the assignment's fixed test levels. Returns (corrupted, description of what was applied)."""
    i = severity - 1
    if kind == "salt_and_pepper":
        return salt_pepper(x, SP_LEVELS[i], np.random.default_rng(seed)), {"type": kind, "severity": severity, "p": SP_LEVELS[i]}
    if kind == "gaussian_blur":
        k, s = BLUR_LEVELS[i]
        return gaussian_blur(x, k, s), {"type": kind, "severity": severity, "kernel": k, "sigma": s}
    n, f = OCC_LEVELS[i]
    return occlusion(x, n, f, random.Random(seed)), {"type": kind, "severity": severity, "rectangles": n, "area_fraction": f}
