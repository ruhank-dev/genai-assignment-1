"""Specialists reuse the Task 1 autoencoder topology (plan Alternative 1/2) with independent weights."""
from src.task1.autoencoder import UniversalAutoencoder as SpecialistAutoencoder  # noqa: F401

CHANNELS = {"shallow": [32, 64, 128], "standard": [32, 64, 128, 256], "deep": [64, 128, 256]}
SPEC_TYPES = ["salt_pepper", "blur", "occlusion"]
SPEC_FILES = {t: f"specialist_{n}_best.pt" for t, n in zip(SPEC_TYPES, ("salt", "blur", "occlusion"))}
