from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from aiva.database.session import engine
from aiva.modules.camera import module as camera_module


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    yield
    await engine.dispose()


app = FastAPI(
    title="AIVA API",
    description="AI Video Analytics API",
    version="0.1.0",
    lifespan=lifespan,
)

camera_module.register(app)


@app.get("/api/v1/health")
async def health_check():
    return {
        "status": "ok",
    }