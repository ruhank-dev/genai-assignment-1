"""Download Oxford-IIIT Pet via torchvision and validate layout."""
from torchvision.datasets import OxfordIIITPet

from src.shared.config import settings

if __name__ == "__main__":
    for split in ("trainval", "test"):
        ds = OxfordIIITPet(root=str(settings.data_dir), split=split, target_types="category", download=True)
        print(split, len(ds))
    base = settings.data_dir / "oxford-iiit-pet"
    assert (base / "images").is_dir() and (base / "annotations").is_dir()
    print("OK", base)
