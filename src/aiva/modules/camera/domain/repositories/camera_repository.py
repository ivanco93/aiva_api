from typing import Protocol

from aiva.modules.camera.domain.entities.camera import Camera
from aiva.modules.camera.domain.enums.camera_source_type import CameraSourceType
from aiva.modules.camera.domain.enums.camera_status import CameraStatus


class CameraRepository(Protocol):
    async def find_by_id(self, camera_id: int) -> Camera | None: ...

    async def find_by_code(self, code: str) -> Camera | None: ...

    async def search(
        self,
        *,
        name: str | None = None,
        code: str | None = None,
        location_id: int | None = None,
        status: CameraStatus | None = None,
        source_type: CameraSourceType | None = None,
        offset: int = 0,
        limit: int = 20,
    ) -> tuple[list[Camera], int]:
        """Devuelve la página pedida y el total de filas que cumplen los filtros."""
        ...

    async def save(self, camera: Camera) -> Camera:
        """Inserta si la cámara no tiene id, si no la actualiza. Devuelve el estado persistido."""
        ...

    async def delete(self, camera_id: int) -> None: ...
