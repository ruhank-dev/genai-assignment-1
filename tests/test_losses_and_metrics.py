import torch

from src.shared.losses import l1_loss, rec_loss, ssim_loss
from src.shared.metrics import batch_metrics
from src.shared.visualization import make_error_heatmap, make_reconstruction_grid


def test_identical():
    y = torch.rand(2, 3, 128, 128)
    assert l1_loss(y, y) == 0
    assert ssim_loss(y, y).abs() < 1e-5
    m = batch_metrics(y, y)
    assert m["ssim"] > 0.9999 and m["psnr"] >= 79.99  # eps=1e-8 caps PSNR at exactly 80 dB


def test_different_is_worse():
    y = torch.rand(2, 3, 128, 128)
    m = batch_metrics(y, 1 - y)
    assert m["psnr"] < 20 and m["ssim"] < 0.5 and m["l1"] > 0.1


def test_backward():
    y = torch.rand(2, 3, 128, 128)
    yh = torch.rand(2, 3, 128, 128, requires_grad=True)
    rec_loss(y, yh, 0.8).backward()
    assert torch.isfinite(yh.grad).all() and yh.grad.abs().sum() > 0


def test_viz_shapes():
    a = torch.rand(8, 3, 128, 128)
    assert make_reconstruction_grid(a, a, a).shape[0] == 3
    assert make_error_heatmap(a, a).shape == (8, 3, 128, 128)
