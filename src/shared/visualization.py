import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import torch
from matplotlib import colormaps
from torchvision.utils import make_grid


def make_reconstruction_grid(corrupted, restored, target, n_samples: int = 8) -> torch.Tensor:
    rows = [t[:n_samples].detach().cpu().clamp(0, 1) for t in (corrupted, restored, target)]
    return make_grid(torch.cat(rows), nrow=min(n_samples, rows[0].shape[0]), padding=2)


def make_error_heatmap(restored, target, vmax: float = 0.5, cmap: str = "inferno") -> torch.Tensor:
    err = (target - restored).abs().mean(1).detach().cpu().clamp(0, vmax) / vmax  # (B,H,W)
    rgb = colormaps[cmap](err.numpy())[..., :3]
    return torch.from_numpy(rgb).float().permute(0, 3, 1, 2)


def plot_training_curves(history: dict):
    """history: {metric_name: list}; pairs 'train_X'/'val_X' share a panel."""
    names = sorted({k.split("_", 1)[1] for k in history if k.startswith(("train_", "val_"))})
    fig, axes = plt.subplots(1, max(1, len(names)), figsize=(4.5 * max(1, len(names)), 3.5))
    axes = [axes] if len(names) <= 1 else list(axes)
    for ax, n in zip(axes, names):
        for pre in ("train", "val"):
            if f"{pre}_{n}" in history:
                ax.plot(history[f"{pre}_{n}"], label=pre)
        ax.set_title(n)
        ax.set_xlabel("epoch")
        ax.legend()
        ax.grid(alpha=0.3)
    fig.tight_layout()
    return fig
