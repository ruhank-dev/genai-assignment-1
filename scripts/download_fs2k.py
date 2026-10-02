"""Download FS2K (Google Drive, via gdown), unzip, and verify 1:1 photo<->sketch pairing."""
import json
import zipfile

import gdown

from src.shared.config import settings
from src.shared.datasets.fs2k import pair_paths

GDRIVE_ID = "1saIMhQ3dc5_ftkfGmBPbCluRn_zy7QQp"

if __name__ == "__main__":
    root = settings.data_dir / "fs2k"
    root.mkdir(parents=True, exist_ok=True)
    zp = root / "FS2K.zip"
    if not (root / "FS2K" / "anno_train.json").exists():
        if not zp.exists():
            gdown.download(id=GDRIVE_ID, output=str(zp))
        zipfile.ZipFile(zp).extractall(root)
    total = 0
    for split in ("train", "test"):
        n = len(pair_paths(split))  # asserts every pair exists
        print(split, n)
        total += n
    assert total == 2104, total
    print("OK: 2104 pairs verified")
