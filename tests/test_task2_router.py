import torch

from src.task2.classifier import CorruptionClassifier
from src.task2.router import EXPERTS, HardRouter
from src.task1.autoencoder import UniversalAutoencoder


def make():
    torch.manual_seed(0)
    cls = CorruptionClassifier([16, 32], 0.0).eval()
    specs = [UniversalAutoencoder([32, 64, 128], 64).eval() for _ in range(3)]
    return HardRouter(cls, specs).eval()


def test_identity_bypass_exact_and_batch_order():
    r = make()
    x = torch.rand(6, 3, 128, 128)
    labels = torch.tensor([0, 1, 2, 3, 0, 2])
    out = r(x, oracle_labels=labels)["reconstructed"]
    assert out.shape == x.shape
    assert torch.equal(out[0], x[0]) and torch.equal(out[4], x[4])  # MSE == 0 for clean
    for i, k in enumerate(labels.tolist()):  # order preserved: row i equals expert k applied to x[i] alone
        if k:
            assert torch.allclose(out[i], r.specialists[k - 1](x[i:i + 1])[0], atol=1e-5)


def test_single_image_fields():
    r = make()
    o = r(torch.rand(1, 3, 128, 128))
    assert o["selected_expert"] in EXPERTS and abs(sum(o["probabilities"].values()) - 1) < 1e-5
    assert o["total_latency_ms"] >= o["classifier_latency_ms"] >= 0
