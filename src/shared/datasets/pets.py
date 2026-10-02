"""Oxford-IIIT Pet with deterministic stratified 80/20 train/val split (seed 42)."""
from pathlib import Path
from typing import Callable, Optional

import numpy as np
import torch
from PIL import Image
from sklearn.model_selection import train_test_split
from torch.utils.data import Dataset
from torchvision.datasets import OxfordIIITPet

from src.shared.config import settings


def _split_indices(labels: list[int], seed: int = 42) -> tuple[list[int], list[int]]:
    idx = np.arange(len(labels))
    tr, va = train_test_split(idx, test_size=0.2, random_state=seed, stratify=labels)
    return sorted(tr.tolist()), sorted(va.tolist())


class PetDataset(Dataset):
    """Returns clean (3,128,128) float32 in [0,1] (+ breed label if return_labels)."""

    def __init__(self, root: Optional[Path] = None, split: str = "train",
                 transform: Optional[Callable] = None, return_labels: bool = False, size: int = 128):
        assert split in ("train", "val", "test")
        root = root or settings.data_dir
        self.base = OxfordIIITPet(root=str(root), split="test" if split == "test" else "trainval",
                                  target_types="category", download=False)
        self.paths = list(self.base._images)
        self.labels = list(self.base._labels)
        if split != "test":
            tr, va = _split_indices(self.labels, settings.seed)
            keep = tr if split == "train" else va
            self.paths = [self.paths[i] for i in keep]
            self.labels = [self.labels[i] for i in keep]
        self.split, self.transform, self.return_labels, self.size = split, transform, return_labels, size
        self.classes = self.base.classes

    def __len__(self) -> int:
        return len(self.paths)

    def _cache(self) -> np.ndarray:
        """uint8 (N,H,W,3) memmap of RGB-converted, bicubic-resized images (built once, shared by workers)."""
        f = settings.data_dir / "cache" / f"pets_{self.split}_{self.size}.npy"
        if not f.exists():
            f.parent.mkdir(parents=True, exist_ok=True)
            arr = np.stack([np.asarray(Image.open(p).convert("RGB").resize((self.size, self.size), Image.BICUBIC))
                            for p in self.paths])
            np.save(f, arr)
        return np.load(f, mmap_mode="r")

    def load(self, i: int) -> torch.Tensor:
        if not hasattr(self, "_arr"):
            self._arr = self._cache()
        return torch.from_numpy(np.array(self._arr[i], dtype=np.float32) / 255.0).permute(2, 0, 1).contiguous()

    def __getitem__(self, i: int):
        x = self.load(i)
        if self.transform:
            x = self.transform(x)
        return (x, self.labels[i]) if self.return_labels else x
