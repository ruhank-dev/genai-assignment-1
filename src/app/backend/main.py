from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.app.backend.config import settings
from src.app.backend.routers import health, task1, task2, task3, task4
from src.app.backend.services.inference import ModelRegistry


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.registry = ModelRegistry()
    app.state.registry.load()  # sessions are created once at start-up, never per request
    yield


app = FastAPI(title="GenAI Assignment 1 - Restoration & Sketch API", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origins, allow_methods=["*"], allow_headers=["*"])
for r in (health.router, task1.router, task2.router, task3.router, task4.router):
    app.include_router(r)
