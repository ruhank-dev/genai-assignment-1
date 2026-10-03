import torch
import torch.nn as nn

from src.task3.gate import GatingNetwork


class SoftMoE(nn.Module):
    """x_hat = w1*x + w2*A_salt(x) + w3*A_blur(x) + w4*A_occ(x), w = softmax(G(x)/tau). Identity branch has no params."""

    def __init__(self, gate: GatingNetwork, salt: nn.Module, blur: nn.Module, occlusion: nn.Module):
        super().__init__()
        self.gate, self.salt_expert, self.blur_expert, self.occlusion_expert = gate, salt, blur, occlusion

    @property
    def experts(self) -> nn.ModuleList:
        return nn.ModuleList([self.salt_expert, self.blur_expert, self.occlusion_expert])

    def forward(self, x: torch.Tensor, tau: float = 1.0):
        z, w = self.gate(x, tau)
        branches = torch.stack([x, self.salt_expert(x), self.blur_expert(x), self.occlusion_expert(x)], dim=1)  # B,4,C,H,W
        out = (w[:, :, None, None, None] * branches).sum(dim=1)
        return out, w, z
