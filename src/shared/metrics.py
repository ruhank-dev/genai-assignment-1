import torch
from pytorch_msssim import ssim


@torch.no_grad()
def psnr_per_image(y: torch.Tensor, yhat: torch.Tensor, eps: float = 1e-8) -> torch.Tensor:
    mse = ((y - yhat) ** 2).flatten(1).mean(1)
    return 10 * torch.log10(1.0 / (mse + eps))


@torch.no_grad()
def ssim_per_image(y: torch.Tensor, yhat: torch.Tensor) -> torch.Tensor:
    return ssim(yhat.float(), y.float(), data_range=1.0, size_average=False)


@torch.no_grad()
def l1_per_image(y: torch.Tensor, yhat: torch.Tensor) -> torch.Tensor:
    return (y - yhat).abs().flatten(1).mean(1)


@torch.no_grad()
def batch_metrics(y: torch.Tensor, yhat: torch.Tensor) -> dict:
    return {"psnr": psnr_per_image(y, yhat).mean().item(), "ssim": ssim_per_image(y, yhat).mean().item(),
            "l1": l1_per_image(y, yhat).mean().item()}
