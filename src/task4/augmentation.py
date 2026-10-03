"""Paired augmentation: every spatial operation uses ONE random draw applied to both photo and sketch.
Photometric jitter touches the photo only (sketch line intensity must stay untouched). Tensors are in [-1, 1]."""
import math
import random

import torch
import torch.nn.functional as F


class PairedAugment:
    def __init__(self, flip_p: float = 0.5, max_shift: int = 8, max_rot_deg: float = 10.0, photo_jitter: float = 0.15,
                 seed: int | None = None):
        self.flip_p, self.max_shift, self.max_rot, self.jitter = flip_p, max_shift, max_rot_deg, photo_jitter
        self.rng = random.Random(seed)

    def draw(self) -> dict:
        r = self.rng
        return {"flip": r.random() < self.flip_p, "dx": r.randint(-self.max_shift, self.max_shift),
                "dy": r.randint(-self.max_shift, self.max_shift), "rot": r.uniform(-self.max_rot, self.max_rot),
                "bright": r.uniform(-self.jitter, self.jitter), "contrast": 1 + r.uniform(-self.jitter, self.jitter)}

    @staticmethod
    def spatial(x: torch.Tensor, p: dict) -> torch.Tensor:
        """Flip + rotation + translation (equivalent to padded random crop) as a single affine warp."""
        if p["flip"]:
            x = x.flip(-1)
        h, w = x.shape[-2:]
        a = math.radians(p["rot"])
        theta = torch.tensor([[math.cos(a), -math.sin(a), 2 * p["dx"] / w],
                              [math.sin(a), math.cos(a), 2 * p["dy"] / h]], dtype=x.dtype)
        grid = F.affine_grid(theta[None], (1, *x.shape), align_corners=False)
        return F.grid_sample(x[None], grid, mode="bilinear", padding_mode="border", align_corners=False)[0]

    def __call__(self, photo: torch.Tensor, sketch: torch.Tensor):
        p = self.draw()
        photo, sketch = self.spatial(photo, p), self.spatial(sketch, p)
        photo = ((photo - photo.mean()) * p["contrast"] + photo.mean() + p["bright"]).clamp(-1, 1)  # photo only
        return photo, sketch
