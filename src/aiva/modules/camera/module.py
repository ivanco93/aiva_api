from fastapi import FastAPI

from aiva.modules.camera.infrastructure.http.exception_handlers import register_exception_handlers
from aiva.modules.camera.infrastructure.http.routers.camera_router import router as camera_router
from aiva.modules.camera.infrastructure.http.routers.health_router import router as health_router


def register(app: FastAPI) -> None:
    app.include_router(health_router, prefix="/api/v1")
    app.include_router(camera_router, prefix="/api/v1")
    register_exception_handlers(app)
