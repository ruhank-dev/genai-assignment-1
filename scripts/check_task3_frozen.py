"""Warm-up (experts frozen) must leave expert weights bit-exact equal to the Task 2 checkpoints."""
import torch

from src.shared.config import settings
from src.task2.specialist import SPEC_FILES, SPEC_TYPES
from src.task3.train import BASELINE, run_training

if __name__ == "__main__":  # guard needed: DataLoader workers re-import __main__ on Windows
    run_training(BASELINE, 1, 0, settings.checkpoint_dir / "task3" / "frozen_check", "m.pth", "genai-task3-soft-moe", "frozen-check")
    sd = torch.load(settings.checkpoint_dir / "task3" / "frozen_check" / "latest.pth", map_location="cpu")["model_state_dict"]
    for t, name in zip(SPEC_TYPES, ("salt_expert", "blur_expert", "occlusion_expert")):
        ref = torch.load(settings.checkpoint_dir / "task2" / SPEC_FILES[t], map_location="cpu")["model_state_dict"]
        ok = all(torch.equal(sd[f"{name}.{k}"], v) for k, v in ref.items())
        print(name, "bit-exact:", ok)
        assert ok
