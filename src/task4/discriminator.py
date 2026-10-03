import torch
import torch.nn as nn


class PatchDiscriminator(nn.Module):
    """D(x, y, s): PatchGAN over concat[photo, sketch, replicated style embedding]; returns raw patch logits (no sigmoid).
    n_layers=3 -> 70x70 receptive field (pix2pix default), n_layers=1 -> 16x16, n_layers=2 -> 34x34."""

    def __init__(self, base: int = 64, emb_dim: int = 16, n_layers: int = 3, n_styles: int = 3):
        super().__init__()
        self.cfg = dict(base=base, emb_dim=emb_dim, n_layers=n_layers)
        self.emb = nn.Embedding(n_styles, emb_dim)
        layers = [nn.Conv2d(6 + emb_dim, base, 4, 2, 1), nn.LeakyReLU(0.2, True)]
        c = base
        for i in range(1, n_layers):
            layers += [nn.Conv2d(c, min(c * 2, 8 * base), 4, 2, 1, bias=False), nn.InstanceNorm2d(min(c * 2, 8 * base)),
                       nn.LeakyReLU(0.2, True)]
            c = min(c * 2, 8 * base)
        layers += [nn.Conv2d(c, min(c * 2, 8 * base), 4, 1, 1, bias=False), nn.InstanceNorm2d(min(c * 2, 8 * base)),
                   nn.LeakyReLU(0.2, True)]
        c = min(c * 2, 8 * base)
        layers += [nn.Conv2d(c, 1, 4, 1, 1)]
        self.net = nn.Sequential(*layers)
        self.apply(lambda m: nn.init.normal_(m.weight, 0.0, 0.02) if isinstance(m, nn.Conv2d) else None)

    def forward(self, photo: torch.Tensor, sketch: torch.Tensor, style: torch.Tensor) -> torch.Tensor:
        e = self.emb(style)[:, :, None, None].expand(-1, -1, *photo.shape[-2:])
        return self.net(torch.cat([photo, sketch, e], dim=1))
