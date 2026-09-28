from dataclasses import replace
from datetime import datetime

from aiva.modules.camera.domain.entities.camera import Camera
from aiva.modules.camera.domain.enums.camera_source_type import CameraSourceType
from aiva.modules.camera.domain.enums.camera_status import CameraStatus


class InMemoryCameraRepository:
    """Guarda copias para que, como en la BD real, mutar una entidad leída no altere lo persistido."""

    def __init__(self) -> None:
        self._rows: dict[int, Camera] = {}
        self._next_id = 1

    async def find_by_id(self, camera_id: int) -> Camera | None:
        camera = self._rows.get(camera_id)
        return replace(camera) if camera else None

    async def find_by_code(self, code: str) -> Camera | None:
        camera = next((c for c in self._rows.values() if c.code == code), None)
        return replace(camera) if camera else None

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
        rows = [
            c
            for c in sorted(self._rows.values(), key=lambda c: c.id or 0)
            if (not name or name in c.name)
            and (not code or c.code == code)
            and (location_id is None or c.location_id == location_id)
            and (status is None or c.status == status)
            and (source_type is None or c.source.source_type == source_type)
        ]
        return [replace(c) for c in rows[offset : offset + limit]], len(rows)

    async def save(self, camera: Camera) -> Camera:
        now = datetime(2026, 1, 1)
        if camera.id is None:
            stored = replace(camera, id=self._next_id, created_at=now)
            self._next_id += 1
        else:
            stored = replace(camera, updated_at=now)
        self._rows[stored.id] = stored
        return replace(stored)

    async def delete(self, camera_id: int) -> None:
        self._rows.pop(camera_id, None)
