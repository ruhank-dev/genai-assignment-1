"""Deterministic validation/test corruption manifests (parameter primitives only)."""
import json
import random
from pathlib import Path

from src.shared.config import settings
from src.shared.corruptions import TYPES, sample_params


def build_val_manifest(n: int, seed: int = 42) -> list[dict]:
    rng = random.Random(seed)
    types = [TYPES[i % 4] for i in range(n)]  # exactly 25% each (n divisible by 4)
    rng.shuffle(types)
    out = []
    for i, t in enumerate(types):
        p = sample_params(t, rng)
        out.append({"idx": i, "label": TYPES.index(t), **p})
    return out


def build_test_manifest(n: int, seed: int = 42) -> list[dict]:
    rng = random.Random(seed + 1)
    out = []
    for i in range(n):
        out.append({"idx": i, "label": 0, **sample_params("clean", rng)})
        for ci, t in enumerate(TYPES[1:], start=1):
            for lvl in (1, 2, 3):
                out.append({"idx": i, "label": ci, **sample_params(t, rng, lvl)})
    return out  # 10 entries per image


def save(manifest: list[dict], name: str) -> Path:
    settings.manifest_dir.mkdir(exist_ok=True, parents=True)
    path = settings.manifest_dir / name
    path.write_text(json.dumps(manifest, separators=(",", ":")))
    return path


def load(name: str) -> list[dict]:
    return json.loads((settings.manifest_dir / name).read_text())
