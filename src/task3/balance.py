"""Routing-balance regularizers (Step 4 alternatives). All take w: (B,4) routing weights, return a scalar."""
import torch


def l2_balance(w: torch.Tensor) -> torch.Tensor:
    """Assignment form: sum_k (mean_i w_ik - 1/4)^2 (0 when the batch-mean routing is uniform)."""
    return ((w.mean(0) - 0.25) ** 2).sum()


def entropy_balance(w: torch.Tensor, eps: float = 1e-8) -> torch.Tensor:
    """Negative entropy of the batch-mean routing, shifted by log(4) so the minimum is 0."""
    m = w.mean(0)
    return (m * torch.log(m + eps)).sum() + torch.log(torch.tensor(4.0, device=w.device))


def switch_balance(w: torch.Tensor) -> torch.Tensor:
    """Switch-Transformer load balancing: 4 * sum_k f_k * mean_w_k (f_k = hard assignment fraction, non-differentiable)."""
    f = torch.nn.functional.one_hot(w.argmax(1), 4).float().mean(0)
    return 4 * (f * w.mean(0)).sum() - 1.0  # shifted so a perfectly balanced batch gives 0


BALANCE = {"l2": l2_balance, "entropy": entropy_balance, "switch": switch_balance}
