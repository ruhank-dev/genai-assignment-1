import torch
import torch.nn as nn


class Down(nn.Module):
    def __init__(self, cin: int, cout: int, norm: bool = True):
        super().__init__()
        layers = [nn.Conv2d(cin, cout, 4, 2, 1, bias=not norm)]
        if norm:
            layers.append(nn.InstanceNorm2d(cout))
        layers.append(nn.LeakyReLU(0.2, True))
        self.net = nn.Sequential(*layers)

    def forward(self, x):
        return self.net(x)


class Up(nn.Module):
    """ConvTranspose -> InstanceNorm -> (FiLM: gamma(s)*h + beta(s)) -> (Dropout) -> ReLU, then concat with the skip."""

    def __init__(self, cin: int, cout: int, emb_dim: int, film: bool, dropout: float = 0.0):
        super().__init__()
        self.conv = nn.ConvTranspose2d(cin, cout, 4, 2, 1, bias=False)
        self.norm = nn.InstanceNorm2d(cout)
        self.film = nn.Linear(emb_dim, 2 * cout) if film else None
        if film:  # start as identity modulation
            nn.init.zeros_(self.film.weight)
            nn.init.zeros_(self.film.bias)
        self.drop = nn.Dropout(dropout) if dropout else nn.Identity()

    def forward(self, x, e, skip=None):
        h = self.norm(self.conv(x))
        if self.film is not None:
            g, b = self.film(e).chunk(2, dim=1)
            h = h * (1 + g[:, :, None, None]) + b[:, :, None, None]
        h = torch.relu(self.drop(h))
        return h if skip is None else torch.cat([h, skip], dim=1)


class UNetGenerator(nn.Module):
    """G(x, s): pix2pix-style U-Net (128 -> 4 -> 128) with a learned style embedding e_s.
    style_mode='film'  : e_s modulates every decoder block (gamma, beta) and is concatenated at the bottleneck.
    style_mode='concat': e_s is replicated spatially and concatenated to the input photo and to the bottleneck."""

    def __init__(self, base: int = 64, emb_dim: int = 16, dropout: float = 0.3, style_mode: str = "film",
                 n_styles: int = 3):
        super().__init__()
        self.cfg = dict(base=base, emb_dim=emb_dim, dropout=dropout, style_mode=style_mode)
        self.mode, self.emb = style_mode, nn.Embedding(n_styles, emb_dim)
        b = base
        cin0 = 3 + (emb_dim if style_mode == "concat" else 0)
        self.d1, self.d2, self.d3 = Down(cin0, b, False), Down(b, 2 * b), Down(2 * b, 4 * b)  # 64,32,16
        self.d4, self.d5 = Down(4 * b, 8 * b), Down(8 * b, 8 * b)  # 8,4
        self.mid = nn.Sequential(nn.Conv2d(8 * b + emb_dim, 8 * b, 3, 1, 1), nn.ReLU(True), nn.Dropout(dropout))
        film = style_mode == "film"
        self.u5 = Up(8 * b, 8 * b, emb_dim, film, dropout)  # 4 -> 8, concat d4
        self.u4 = Up(16 * b, 4 * b, emb_dim, film, dropout)  # 8 -> 16, concat d3
        self.u3 = Up(8 * b, 2 * b, emb_dim, film)  # 16 -> 32, concat d2
        self.u2 = Up(4 * b, b, emb_dim, film)  # 32 -> 64, concat d1
        self.out = nn.Sequential(nn.ConvTranspose2d(2 * b, 3, 4, 2, 1), nn.Tanh())  # 64 -> 128
        self.apply(self._init)

    @staticmethod
    def _init(m):
        if isinstance(m, (nn.Conv2d, nn.ConvTranspose2d)):
            nn.init.normal_(m.weight, 0.0, 0.02)

    def forward(self, photo: torch.Tensor, style: torch.Tensor) -> torch.Tensor:
        e = self.emb(style)  # (B, d)
        x = photo
        if self.mode == "concat":
            x = torch.cat([photo, e[:, :, None, None].expand(-1, -1, *photo.shape[-2:])], 1)
        d1 = self.d1(x)
        d2 = self.d2(d1)
        d3 = self.d3(d2)
        d4 = self.d4(d3)
        d5 = self.d5(d4)
        m = self.mid(torch.cat([d5, e[:, :, None, None].expand(-1, -1, *d5.shape[-2:])], 1))
        h = self.u5(m, e, d4)
        h = self.u4(h, e, d3)
        h = self.u3(h, e, d2)
        h = self.u2(h, e, d1)
        return self.out(h)
