"""NumPy image-quality metrics for the API (no torch): MSE, L1, PSNR (MAX=1, eps 1e-8) and SSIM
(Gaussian 11x11 window, sigma 1.5, 'valid' region - the same definition as pytorch-msssim used in training)."""
import numpy as np
from numpy.lib.stride_tricks import sliding_window_view

_C1, _C2 = 0.01 ** 2, 0.03 ** 2


def _window(size: int = 11, sigma: float = 1.5) -> np.ndarray:
    ax = np.arange(size) - (size - 1) / 2
    g = np.exp(-(ax ** 2) / (2 * sigma ** 2))
    g /= g.sum()
    return np.outer(g, g)


_W = _window()


def _filt(x: np.ndarray) -> np.ndarray:
    return np.einsum("ijkl,kl->ij", sliding_window_view(x, _W.shape), _W)


def mse(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.mean((a.astype(np.float64) - b) ** 2))


def psnr(a: np.ndarray, b: np.ndarray) -> float:
    return float(10 * np.log10(1.0 / (mse(a, b) + 1e-8)))


def ssim(a: np.ndarray, b: np.ndarray) -> float:
    """a, b: (C,H,W) float in [0,1]; mean SSIM over channels and positions."""
    vals = []
    for x, y in zip(a.astype(np.float64), b.astype(np.float64)):
        mx, my = _filt(x), _filt(y)
        sxx, syy, sxy = _filt(x * x) - mx * mx, _filt(y * y) - my * my, _filt(x * y) - mx * my
        vals.append(np.mean(((2 * mx * my + _C1) * (2 * sxy + _C2)) / ((mx ** 2 + my ** 2 + _C1) * (sxx + syy + _C2))))
    return float(np.mean(vals))


def all_metrics(restored: np.ndarray, reference: np.ndarray) -> dict:
    return {"psnr": psnr(restored, reference), "ssim": ssim(restored, reference), "mse": mse(restored, reference),
            "l1": float(np.abs(restored - reference).mean())}
