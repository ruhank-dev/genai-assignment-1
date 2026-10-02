"""FS2K paired photo/sketch dataset. Official train/test; 15% of train -> val, stratified by style, seed 42."""
import json
from pathlib import Path
from typing import Callable, Optional

import numpy as np
import torch
from PIL import Image
from sklearn.model_selection import train_test_split
from torch.utils.data import Dataset

from src.shared.config import settings


def _find(p: Path) -> Path:
    for ext in (".jpg", ".png", ".jpeg"):
        if p.with_suffix(ext).exists():
            return p.with_suffix(ext)
    raise AssertionError(f"missing image {p}")


def pair_paths(split: str, root: Path | None = None) -> list[tuple[Path, Path, int]]:
    """Official split ('train'/'test') -> [(photo, sketch, style)]; asserts a sketch exists for every photo."""
    base = (root or settings.data_dir / "fs2k") / "FS2K"
    out = []
    for a in json.loads((base / f"anno_{split}.json").read_text()):
        grp, name = a["image_name"].split("/")  # photo1/image0110
        photo = _find(base / "photo" / grp / name)
        sketch = _find(base / "sketch" / grp.replace("photo", "sketch") / name.replace("image", "sketch"))
        out.append((photo, sketch, int(a["style"])))
    return out


class FS2KDataset(Dataset):
    """Item -> (photo, sketch, style_id) in [-1,1], 3x128x128. `transform(photo, sketch)` must be paired."""

    def __init__(self, split: str = "train", root: Optional[Path] = None,
                 transform: Optional[Callable] = None, size: int = 128):
        assert split in ("train", "val", "test")
        items = pair_paths("test" if split == "test" else "train", root)
        if split != "test":
            idx = np.arange(len(items))
            tr, va = train_test_split(idx, test_size=0.15, random_state=settings.seed,
                                      stratify=[s for _, _, s in items])
            items = [items[i] for i in sorted((tr if split == "train" else va).tolist())]
        self.items, self.transform, self.size, self.split = items, transform, size, split
        self.styles = [s for _, _, s in items]
        self.photos = torch.stack([self._load(p) for p, _, _ in items])  # tiny dataset: cache in RAM
        self.sketches = torch.stack([self._load(s) for _, s, _ in items])

    def _load(self, path: Path) -> torch.Tensor:
        img = Image.open(path).convert("RGB").resize((self.size, self.size), Image.BICUBIC)
        return torch.from_numpy(np.asarray(img, dtype=np.float32) / 127.5 - 1.0).permute(2, 0, 1).contiguous()

    def __len__(self) -> int:
        return len(self.items)

    def __getitem__(self, i: int):
        x, y = self.photos[i], self.sketches[i]
        if self.transform:
            x, y = self.transform(x, y)
        return x, y, self.styles[i]
