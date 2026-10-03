import random

import pytest
import torch

from src.task4.augmentation import PairedAugment
from src.task4.discriminator import PatchDiscriminator
from src.task4.generator import UNetGenerator


@pytest.mark.parametrize("mode", ["film", "concat"])
def test_generator_shape_range_and_style_dependence(mode):
    g = UNetGenerator(base=16, emb_dim=8, style_mode=mode).eval()
    nn_init = torch.nn.init.normal_
    for p in g.emb.parameters():  # make embeddings clearly different so FiLM/concat has a visible effect
        nn_init(p, 0, 1)
    if mode == "film":
        for m in g.modules():
            if hasattr(m, "film") and m.film is not None:
                nn_init(m.film.weight, 0, 0.1)
    x = torch.rand(3, 3, 128, 128) * 2 - 1
    y0 = g(x, torch.zeros(3, dtype=torch.long))
    y1 = g(x, torch.ones(3, dtype=torch.long))
    assert y0.shape == (3, 3, 128, 128) and y0.abs().max() <= 1.0
    assert (y0 - y1).abs().mean() > 1e-4  # the style condition actually changes the output


@pytest.mark.parametrize("n_layers,expect", [(3, (14, 14)), (1, (62, 62))])
def test_discriminator_logits_shape(n_layers, expect):
    d = PatchDiscriminator(base=16, emb_dim=8, n_layers=n_layers)
    out = d(torch.rand(2, 3, 128, 128), torch.rand(2, 3, 128, 128), torch.tensor([0, 2]))
    assert out.shape == (2, 1, *expect)


def test_style_embedding_gets_gradient_in_G_and_D():
    g, d = UNetGenerator(base=16, emb_dim=8), PatchDiscriminator(base=16, emb_dim=8)
    x, s = torch.rand(2, 3, 128, 128), torch.tensor([0, 1])
    y = g(x, s)
    d(x, y, s).mean().backward()
    assert g.emb.weight.grad is not None and d.emb.weight.grad is not None
    assert g.emb.weight.grad.abs().sum() > 0 and d.emb.weight.grad.abs().sum() > 0


def test_paired_augmentation_is_identical_for_both_images():
    aug = PairedAugment(seed=1)
    x = torch.rand(3, 128, 128) * 2 - 1
    for _ in range(5):
        p = aug.draw()
        a, b = aug.spatial(x, p), aug.spatial(x.clone(), p)  # same image + same params -> same warp
        assert torch.equal(a, b)
    # full pipeline on identical photo/sketch: spatial parts coincide, only the photo gets photometric jitter
    aug = PairedAugment(seed=3, photo_jitter=0.0)
    photo, sketch = aug(x, x.clone())
    assert torch.allclose(photo, sketch, atol=1e-5)
    # flip check: a left-edge marker must move to the right edge in both
    m = torch.zeros(3, 128, 128)
    m[:, :, 0] = 1
    flipped = PairedAugment.spatial(m, {"flip": True, "dx": 0, "dy": 0, "rot": 0.0})
    assert flipped[:, :, -1].mean() > 0.5 and flipped[:, :, 0].mean() < 0.5
    assert random is not None
