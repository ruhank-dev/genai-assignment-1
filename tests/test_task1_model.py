import pytest
import torch

from src.shared.losses import rec_loss
from src.task1.autoencoder import UniversalAutoencoder

CFGS = [[32, 64, 128], [64, 128, 256], [32, 64, 128, 256]]


@pytest.mark.parametrize("ch", CFGS)
def test_shape_range_grad(ch):
    m = UniversalAutoencoder(ch, 128, 0.1)
    x = torch.rand(2, 3, 128, 128)
    y = m(x)
    assert y.shape == x.shape and 0 <= y.min() and y.max() <= 1
    rec_loss(x, y).backward()
    assert all(p.grad is not None and torch.isfinite(p.grad).all() for p in m.parameters())
    assert m.compression_ratio() > 1


def test_overfit_smoke():
    torch.manual_seed(0)
    m, x = UniversalAutoencoder([32, 64, 128, 256], 128), torch.nn.functional.interpolate(torch.rand(4, 3, 8, 8), size=128, mode='bilinear')
    opt = torch.optim.Adam(m.parameters(), 2e-3)
    losses = []
    for _ in range(20):
        opt.zero_grad()
        l = rec_loss(x, m(x))
        l.backward()
        opt.step()
        losses.append(l.item())
    print(losses[0], losses[-1])
    assert losses[-1] < losses[0] * 0.5
