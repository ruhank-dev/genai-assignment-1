import torch
from torchvision.utils import save_image

from src.shared.config import get_device, settings
from src.shared.datasets.fs2k import FS2KDataset
from src.task4.export_onnx import load_generator
from src.task4.train import fixed_grid, fixed_indices

if __name__ == "__main__":
    dev = get_device()
    g = load_generator(settings.checkpoint_dir / "task4" / "baseline_generator.pth", dev)
    ds = FS2KDataset("val")
    save_image(fixed_grid(g, ds, fixed_indices(ds), dev), settings.results_dir / "task4" / "baseline_val_grid.png")
