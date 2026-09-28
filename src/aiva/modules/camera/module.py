from fastapi import FastAPI

from aiva.modules.camera.infrastructure.http.exception_handlers import register_exception_handlers
from aiva.modules.camera.infrastructure.http.routers.camera_router import router as camera_router


def register(app: FastAPI) -> None:
    app.include_router(camera_router, prefix="/api/v1")
    register_exception_handlers(app)
