import torch.nn as nn


def conv_block(cin: int, cout: int, stride: int) -> nn.Sequential:
    return nn.Sequential(nn.Conv2d(cin, cout, 3, stride, 1, bias=False), nn.BatchNorm2d(cout), nn.LeakyReLU(0.1, True))


class Encoder(nn.Module):
    """Progressive /2 downsampling with growing channels, then a 1x1 projection to the bottleneck.
    128 -> 128/2^len(channels). No skip connections leave this module (strict bottleneck)."""

    def __init__(self, channels: list[int], bottleneck_dim: int, dropout: float = 0.0):
        super().__init__()
        layers, cin = [], 3
        for c in channels:
            layers += [conv_block(cin, c, 2), conv_block(c, c, 1)]
            cin = c
        self.features = nn.Sequential(*layers)
        self.to_latent = nn.Sequential(nn.Conv2d(cin, bottleneck_dim, 1), nn.Dropout2d(dropout) if dropout else nn.Identity())

    def forward(self, x):
        return self.to_latent(self.features(x))
