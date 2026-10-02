import random

import torch

from src.shared.corruptions import apply_corruption, occlusion_coverage, sample_params


def test_salt_pepper_fraction():
    x = torch.full((3, 128, 128), 0.5)
    p = sample_params("salt_pepper", random.Random(0), level=3)
    y = apply_corruption(x, p)
    frac = ((y == 0) | (y == 1)).float().mean().item()
    assert abs(frac - 0.15) < 0.01
    assert apply_corruption(x, p).equal(y)  # deterministic


def test_blur_attenuates_high_freq():
    x = torch.rand(3, 128, 128)
    y = apply_corruption(x, sample_params("blur", random.Random(0), level=3))
    assert (y[:, 1:] - y[:, :-1]).abs().mean() < 0.3 * (x[:, 1:] - x[:, :-1]).abs().mean()
    assert abs(y.mean() - x.mean()) < 0.02


def test_occlusion_area():
    for lvl, tgt in [(1, .10), (2, .20), (3, .35)]:
        cov = [occlusion_coverage(sample_params("occlusion", random.Random(s), level=lvl)) for s in range(50)]
        assert abs(sum(cov) / len(cov) - tgt) < 0.04
