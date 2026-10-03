from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT = Path(__file__).resolve().parents[3]  # repo root locally, /app inside the container


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="GENAI_", env_file=".env", extra="ignore")

    model_dir: Path = ROOT / "models" / "onnx"
    host: str = "0.0.0.0"
    port: int = 8000
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:3000", "http://localhost"]
    max_upload_mb: int = 10
    image_size: int = 128


settings = Settings()
