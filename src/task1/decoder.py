import torch.nn as nn

from src.task1.encoder import conv_block


class Decoder(nn.Module):
    """Mirror of the encoder: Upsample(x2)+conv (avoids checkerboard artifacts), 1x1 conv, Sigmoid -> [0,1]."""

    def __init__(self, channels: list[int], bottleneck_dim: int):
        super().__init__()
        rev = channels[::-1]
        layers, cin = [conv_block(bottleneck_dim, rev[0], 1)], rev[0]
        for c in rev[1:] + [rev[-1] // 2]:
            layers += [nn.Upsample(scale_factor=2, mode="bilinear", align_corners=False), conv_block(cin, c, 1), conv_block(c, c, 1)]
            cin = c
        layers += [conv_block(cin, cin, 1), nn.Conv2d(cin, 3, 1), nn.Sigmoid()]
        self.net = nn.Sequential(*layers)

    def forward(self, z):
        return self.net(z)
