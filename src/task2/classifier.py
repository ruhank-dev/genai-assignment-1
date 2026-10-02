import torch.nn as nn

CLS_NAMES = ["clean", "salt_pepper", "blur", "occlusion"]
CHANNELS = {"small": [16, 32, 64], "medium": [32, 64, 128], "large": [32, 64, 128, 256]}


def block(cin: int, cout: int) -> nn.Sequential:
    return nn.Sequential(nn.Conv2d(cin, cout, 3, padding=1, bias=False), nn.BatchNorm2d(cout), nn.ReLU(True),
                         nn.Conv2d(cout, cout, 3, padding=1, bias=False), nn.BatchNorm2d(cout), nn.ReLU(True),
                         nn.MaxPool2d(2))


class CorruptionClassifier(nn.Module):
    """Custom conv stack (Alternative 1): [conv-BN-ReLU]x2 + MaxPool per stage -> GAP -> Dropout -> Linear(4).
    The first stage runs at full resolution so single-pixel salt-and-pepper outliers stay detectable.
    Outputs unnormalised logits. `features` (pooled) + `head` are reused as the Task 3 gate."""

    def __init__(self, channels: list[int], dropout: float = 0.2, n_classes: int = 4):
        super().__init__()
        self.cfg = dict(channels=list(channels), dropout=dropout)
        layers, cin = [], 3
        for c in channels:
            layers.append(block(cin, c))
            cin = c
        self.features = nn.Sequential(*layers, nn.AdaptiveAvgPool2d(1), nn.Flatten())
        self.head = nn.Sequential(nn.Dropout(dropout), nn.Linear(cin, n_classes))

    def forward(self, x):
        return self.head(self.features(x))
