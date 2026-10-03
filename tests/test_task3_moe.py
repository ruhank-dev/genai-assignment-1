import torch

from src.task1.autoencoder import UniversalAutoencoder
from src.task2.classifier import CorruptionClassifier
from src.task3.balance import BALANCE
from src.task3.gate import GatingNetwork
from src.task3.moe_model import SoftMoE


def make():
    torch.manual_seed(0)
    gate = GatingNetwork(CorruptionClassifier([16, 32], 0.0))
    ex = [UniversalAutoencoder([32, 64, 128], 64) for _ in range(3)]
    return SoftMoE(gate, *ex)


def test_shapes_and_simplex():
    m = make().eval()
    x = torch.rand(4, 3, 128, 128)
    out, w, z = m(x, tau=0.7)
    assert out.shape == x.shape and w.shape == (4, 4) and z.shape == (4, 4)
    assert torch.allclose(w.sum(1), torch.ones(4), atol=1e-6)


def test_temperature_clamp_and_sharpness():
    m = make().eval()
    x = torch.rand(2, 3, 128, 128)
    _, w_hot, _ = m(x, tau=0.0)  # clamped to 0.05, must stay finite
    _, w_soft, _ = m(x, tau=5.0)
    assert torch.isfinite(w_hot).all() and w_hot.max() >= w_soft.max()


def test_gradients_reach_gate_and_experts():
    m = make().train()
    x = torch.rand(4, 3, 128, 128)
    out, w, z = m(x)
    (out.mean() + z.mean()).backward()
    for name, p in m.named_parameters():
        assert p.grad is not None and torch.isfinite(p.grad).all(), name


def test_balance_zero_when_uniform():
    w = torch.full((8, 4), 0.25)
    assert BALANCE["l2"](w) == 0 and abs(BALANCE["entropy"](w)) < 1e-6
    skew = torch.tensor([[1.0, 0, 0, 0]] * 8)
    assert BALANCE["l2"](skew) > 0.4 and BALANCE["entropy"](skew) > 1.0
