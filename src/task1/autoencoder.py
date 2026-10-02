import torch.nn as nn

from src.task1.decoder import Decoder
from src.task1.encoder import Encoder


class UniversalAutoencoder(nn.Module):
    """x_hat = D(E(x_corrupt)). Corruption-agnostic. Reused (with other weights) as Task 2/3 specialists."""

    def __init__(self, channels: list[int] = (32, 64, 128, 256), bottleneck_dim: int = 128, dropout: float = 0.0):
        super().__init__()
        self.cfg = dict(channels=list(channels), bottleneck_dim=bottleneck_dim, dropout=dropout)
        self.encoder = Encoder(list(channels), bottleneck_dim, dropout)
        self.decoder = Decoder(list(channels), bottleneck_dim)

    def forward(self, x):
        return self.decoder(self.encoder(x))

    @property
    def n_params(self) -> int:
        return sum(p.numel() for p in self.parameters())

    def compression_ratio(self, size: int = 128) -> float:
        spatial = size // 2 ** len(self.cfg["channels"])
        return 3 * size * size / (self.cfg["bottleneck_dim"] * spatial * spatial)
