import torch
import torch.nn as nn

TAU_MIN = 0.05  # clamp: avoids division by ~0 / softmax overflow


class GatingNetwork(nn.Module):
    """Gate = Task 2 classifier backbone (conv features + GAP) + a head. Option 1 (linear head, copied 1:1 from the
    classifier) is the default; Option 2 ('mlp': D->128->4, random head on the pretrained backbone) is used only in the
    gate comparison experiment. forward returns raw logits z and weights w = softmax(z / tau)."""

    def __init__(self, classifier: nn.Module, head_type: str = "linear"):
        super().__init__()
        self.features = classifier.features
        d = classifier.head[1].in_features
        if head_type == "linear":
            self.head = classifier.head
        elif head_type == "mlp":
            self.head = nn.Sequential(nn.Dropout(0.2), nn.Linear(d, 128), nn.ReLU(True), nn.Linear(128, 4))
        else:
            raise ValueError(head_type)

    def forward(self, x: torch.Tensor, tau: float = 1.0):
        z = self.head(self.features(x))
        return z, torch.softmax(z / max(tau, TAU_MIN), dim=-1)
