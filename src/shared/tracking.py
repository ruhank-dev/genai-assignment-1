"""Thin MLflow facade (decision: MLflow local/offline; see audit_and_explanation.md)."""
import tempfile
from pathlib import Path
from typing import Optional, Union

import mlflow
import numpy as np
import torch
from PIL import Image

from src.shared.config import settings


class ExperimentTracker:
    def __init__(self) -> None:
        mlflow.set_tracking_uri(settings.mlflow_tracking_uri)

    def start_run(self, run_name: str, experiment_name: str, tags: Optional[dict] = None, nested: bool = False):
        mlflow.set_experiment(experiment_name)
        return mlflow.start_run(run_name=run_name, tags=tags, nested=nested)

    def log_params(self, params: dict) -> None:
        mlflow.log_params({k: str(v)[:250] for k, v in params.items()})

    def log_metrics(self, metrics: dict, step: int) -> None:
        mlflow.log_metrics({k: float(v) for k, v in metrics.items()}, step=step)

    def log_image(self, tag: str, image: Union[torch.Tensor, np.ndarray, Image.Image], step: int) -> None:
        if isinstance(image, torch.Tensor):
            image = image.detach().cpu().float().clamp(0, 1)
            image = image.permute(1, 2, 0).numpy() if image.ndim == 3 else image.numpy()
        if isinstance(image, np.ndarray):
            if image.dtype != np.uint8:
                image = (np.clip(image, 0, 1) * 255).astype(np.uint8)
            image = Image.fromarray(image)
        mlflow.log_image(image, key=tag, step=step)

    def log_figure(self, tag: str, fig, step: int) -> None:
        mlflow.log_figure(fig, f"{tag}_step{step}.png")

    def log_artifact(self, path: Union[str, Path]) -> None:
        mlflow.log_artifact(str(path))

    def end_run(self) -> None:
        mlflow.end_run()
