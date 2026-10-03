# GenAI Assignment 1 — Restoration autoencoders, Mixture-of-Experts and a style-conditioned face-to-sketch GAN

**Author:** Muhammad Ruhan Kamran · 23i-0062 · CS-A · AI-4009 Generative AI

Four systems, one web application:

| # | Workspace | Model(s) | Data |
|---|---|---|---|
| 1 | Universal Restoration | single convolutional denoising autoencoder (3.0x bottleneck) | Oxford-IIIT Pet 128x128 |
| 2 | Hard-Routed Restoration | 4-way corruption classifier + 3 specialist autoencoders (+ identity bypass) | Oxford-IIIT Pet |
| 3 | Soft Mixture-of-Experts Restoration | gate (from the classifier) + identity + 3 experts, jointly fine-tuned | Oxford-IIIT Pet |
| 4 | Face-to-Sketch Generator | U-Net generator + PatchGAN discriminator, learned style embedding (FiLM) | FS2K |

Everything (data prep, training, Optuna studies, evaluation, ONNX export, FastAPI backend, React/Tailwind frontend, Docker Compose) is in this repository.

## 1. Run the application (evaluator quick start — Docker only)

Requirements: Docker Desktop (or Docker Engine + Compose v2). No Python/Node needed.

```bash
git clone https://github.com/ruhank-dev/genai-assignment-1.git
cd genai-assignment-1
docker compose up --build        # the single command
```

Open **http://localhost** (frontend). The API (OpenAPI docs) is at http://localhost:8000/docs and health at http://localhost/health.

* The trained ONNX models are in `models/onnx/` (≈97 MB in total, committed directly; the largest, the 77 MB face-to-sketch generator, is below GitHub's 100 MB limit so no Git LFS is needed). Compose mounts that folder read-only into the backend container.
* If a model file is missing the backend still starts; `/health` reports `degraded` and the affected endpoint answers HTTP 503 with an actionable message.
* Stop with `docker compose down`.

What to try in the browser: *Universal Restoration* → pick a sample, choose a corruption + severity, **Restore Image** (input, restored output, error map, inference time). *Hard-Routed* / *Soft MoE* → build a corrupted input with the **Corruption studio** or upload your own image; see classifier probabilities, selected expert, latency split / the four gate weights. *Face-to-Sketch* → upload a face photo or use the webcam, choose Style 1/2/3, **Generate Sketch**, **Download PNG**.

API (all multipart/form-data): `GET /health`, `POST /api/v1/restore/universal` (`image`, optional `apply_corruption`, `corruption_type`, `severity` 1-3), `POST /api/v1/restore/hard-routed`, `POST /api/v1/restore/soft-moe`, `POST /api/v1/sketch/generate` (`image`, `style` 1-3). Uploads: JPEG/PNG only, ≤ 10 MB.

## 2. Local development

```bash
# backend (inference only needs the slim dependency set)
python -m venv .venv && .venv/Scripts/activate        # or: uv sync  (full training environment, CUDA 12.4 PyTorch)
pip install -r requirements-backend.txt
uvicorn src.app.backend.main:app --port 8000 --reload

# frontend
cd src/app/frontend && pnpm install && pnpm dev       # http://localhost:5173 (proxies /api to :8000)
```

Settings come from environment variables with the `GENAI_` prefix (see `.env.example`), e.g. `GENAI_MODEL_DIR`.

## 3. Reproduce the experiments (needs a GPU; developed on a GTX 1660 SUPER, 6 GB)

```bash
uv sync                                                    # torch 2.6.0+cu124, optuna, mlflow, onnx, ...
uv run python -m scripts.download_pets                     # Oxford-IIIT Pet -> data/oxford-iiit-pet
uv run python -m scripts.download_fs2k                     # FS2K (Google Drive, via gdown) -> data/fs2k
uv run python -m scripts.generate_manifests                # deterministic val/test corruption manifests
# Task 1
uv run python -m src.task1.train --epochs 60               # baseline
uv run python -m src.task1.optuna_search --trials 12       # Optuna (SQLite: optuna/optuna_studies.db)
uv run python -m src.task1.train --mode final --epochs 80 --patience 100
uv run python -m src.task1.evaluate && uv run python -m src.task1.export_onnx
# Task 2
uv run python -m src.task2.optuna_classifier && uv run python -m src.task2.train_classifier --mode final --epochs 15
uv run python -m src.task2.optuna_specialists && uv run python -m src.task2.train_specialists --mode final --epochs 40
uv run python -m src.task2.evaluate && uv run python -m src.task2.export_onnx
# Task 3
uv run python -m src.task3.optuna_search && uv run python -m src.task3.train --mode final --warmup 10 --joint 40
uv run python -m src.task3.routing_analysis && uv run python -m src.task3.evaluate && uv run python -m src.task3.export_onnx
# Task 4
uv run python -m src.task4.optuna_search && uv run python -m src.task4.train --mode final --epochs 100
uv run python -m src.task4.evaluate && uv run python -m src.task4.export_onnx
# experiment tracking UI (MLflow, local SQLite store mlflow.db)
uv run mlflow ui --backend-store-uri sqlite:///mlflow.db
```

Checkpoints go to `checkpoints/` (git-ignored; not included — the ONNX exports in `models/onnx/` are what the app needs). Optuna studies live in `optuna/optuna_studies.db`; per-study trial tables and best parameters are exported to `results/task*/`.

## 4. Tests

```bash
uv run pytest -q                       # 37 tests: losses/metrics, corruptions, models, routers, MoE, GAN, ONNX, backend API
python -m scripts.smoke_test http://localhost      # live stack: 14 end-to-end API checks
python scripts/ui_test.py http://localhost         # browser test of the 4 workspaces (pip install playwright; playwright install chromium)
```

## 5. Results (real numbers from this repository's runs; details in `results/`)

Tasks 1-3 on the official Oxford-IIIT Pet **test** set, 10 variants per image (clean + 3 severities x 3 corruptions), mean over the 9 corrupted variants:

| Method | PSNR (dB) | SSIM | ms/sample |
|---|---|---|---|
| Task 1 universal AE | 23.70 | 0.782 | 0.50 |
| Task 2 hard routing (predicted) | 24.23 | 0.790 | 0.91 |
| Task 2 hard routing (oracle) | 24.22 | 0.790 | 0.91 |
| Task 3 soft MoE | 24.73 | 0.819 | 1.93 |

Classifier (test): accuracy 0.9965, macro-F1 0.9942. Task 4 on the FS2K test set (n = 1046): L1 0.100, SSIM 0.498, PSNR 16.14 dB, LPIPS 0.382, FID 102.1. All ONNX models match PyTorch to ≤ 1.9e-5 (max abs error).

## 6. Repository map

```
src/shared/      datasets (Pets, FS2K), corruptions, manifests, losses, metrics, tracking (MLflow), Optuna utils, ONNX utils
src/task1..4/    models, training, Optuna searches, evaluation, ONNX export for each task
src/app/backend  FastAPI service (routers/, schemas/, services/)       src/app/frontend  React + Vite + Tailwind SPA
models/onnx/     exported inference models           manifests/   deterministic validation/test corruption manifests
results/         metrics, tables, figures, Optuna exports, app screenshots (results/app/)
tests/ scripts/  unit & API tests; data download, smoke/UI tests    Dockerfile.* nginx.conf docker-compose.yml
```

## 7. Notes and honest limitations

* Training budgets were reduced to fit one 6 GB GPU (e.g. 12 Optuna trials per search instead of 30-50); every reduction is documented in the experiment notes.
* The face-to-sketch outputs are recognisable but softer than the ground-truth sketches (L1-dominated loss, 899 training pairs).
* The soft MoE cannot reproduce clean images exactly (a Task-2 identity bypass can) and loses to hard routing on low-severity occlusion; see the analysis in the report.
* The Google Stitch design evidence and the demonstration video required by the assignment are produced outside this repository.
* Third-party assets: Oxford-IIIT Pet (CC BY-SA 4.0 images), FS2K (research use).
