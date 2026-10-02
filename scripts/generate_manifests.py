from src.shared.datasets.pets import PetDataset
from src.shared.manifests import build_test_manifest, build_val_manifest, save

if __name__ == "__main__":
    nv, nt = len(PetDataset(split="val")), len(PetDataset(split="test"))
    v, t = build_val_manifest(nv), build_test_manifest(nt)
    print("val", len(v), save(v, "val_manifest.json").stat().st_size // 1024, "KB")
    print("test", len(t), save(t, "test_manifest.json").stat().st_size // 1024, "KB")
