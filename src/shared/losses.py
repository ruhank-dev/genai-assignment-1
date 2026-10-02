import torch
import torch.nn.functional as F
from pytorch_msssim import ssim


def l1_loss(y: torch.Tensor, yhat: torch.Tensor) -> torch.Tensor:
    return F.l1_loss(yhat, y)


def ssim_loss(y: torch.Tensor, yhat: torch.Tensor) -> torch.Tensor:
    """1 - SSIM, 11x11 Gaussian window (sigma 1.5), data range 1."""
    return 1.0 - ssim(yhat.float(), y.float(), data_range=1.0, size_average=True)


def rec_loss(y: torch.Tensor, yhat: torch.Tensor, alpha: float = 0.8) -> torch.Tensor:
    return alpha * l1_loss(y, yhat) + (1 - alpha) * ssim_loss(y, yhat)
