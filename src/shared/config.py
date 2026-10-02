"""Single source of truth for runtime config, device selection and seeding."""
import random
from pathlib import Path

import numpy as np
import torch
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="GENAI_", env_file=".env", extra="ignore")

    device: str = "auto"
    seed: int = 42
    image_size: int = 128
    num_workers: int = 2
    data_dir: Path = ROOT / "data"
    checkpoint_dir: Path = ROOT / "checkpoints"
    manifest_dir: Path = ROOT / "manifests"
    results_dir: Path = ROOT / "results"
    onnx_dir: Path = ROOT / "models" / "onnx"
    optuna_dir: Path = ROOT / "optuna"
    mlflow_tracking_uri: str = f"sqlite:///{(ROOT / 'mlflow.db').as_posix()}"


settings = Settings()


def get_device() -> torch.device:
    if settings.device != "auto":
        return torch.device(settings.device)
    return torch.device("cuda" if torch.cuda.is_available() else "cpu")


def seed_everything(seed: int | None = None) -> None:
    seed = settings.seed if seed is None else seed
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False
