"""Wraps PetDataset. train: runtime random corruption; val/test: manifest-driven."""
import random

import torch
from torch.utils.data import Dataset, Sampler

from src.shared import manifests
from src.shared.corruptions import TYPES, apply_corruption, sample_params
from src.shared.datasets.pets import PetDataset


class CorruptedPets(Dataset):
    """Item -> (corrupted, clean, label, severity).

    mode='train': per-load random type (uniform over `types`) and params.
    balanced=True: index space is img*4+type so BalancedBatchSampler can give exact class balance.
    """

    def __init__(self, split: str, types: list[str] | None = None, balanced: bool = False):
        self.split = split
        self.base = PetDataset(split=split)
        self.types = types or TYPES
        self.balanced = balanced
        self.manifest = manifests.load(f"{split}_manifest.json") if split in ("val", "test") else None
        if self.manifest is not None and types is not None:  # specialist evaluation: only its corruption
            self.manifest = [m for m in self.manifest if TYPES[m["label"]] in types]

    def __len__(self) -> int:
        if self.manifest is not None:
            return len(self.manifest)
        return len(self.base) * (4 if self.balanced else 1)

    def __getitem__(self, i: int):
        if self.manifest is not None:
            p = self.manifest[i]
            x = self.base.load(p["idx"])
            return apply_corruption(x, p), x, p["label"], p["severity"]
        if self.balanced:
            img, t = divmod(i, 4)
            ctype = TYPES[t]
        else:
            img, ctype = i, random.choice(self.types)
        x = self.base.load(img)
        p = sample_params(ctype, random)
        return apply_corruption(x, p), x, TYPES.index(ctype), 0


class BalancedBatchSampler(Sampler):
    """Each batch has batch_size/4 images per corruption class (exactly balanced)."""

    def __init__(self, n_images: int, batch_size: int, seed: int = 0):
        assert batch_size % 4 == 0
        self.n, self.bs, self.seed, self.epoch = n_images, batch_size, seed, 0

    def __len__(self) -> int:
        return self.n // (self.bs // 4)

    def __iter__(self):
        g = torch.Generator().manual_seed(self.seed + self.epoch)
        self.epoch += 1
        q = self.bs // 4
        for _ in range(len(self)):
            imgs = torch.randint(0, self.n, (4, q), generator=g)
            yield [int(imgs[t, j]) * 4 + t for t in range(4) for j in range(q)]
