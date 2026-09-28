from dataclasses import dataclass
from datetime import datetime
from typing import Self

from aiva.modules.camera.domain.enums.camera_status import CameraStatus
from aiva.modules.camera.domain.exceptions.invalid_camera_error import InvalidCameraError
from aiva.modules.camera.domain.value_objects.camera_source import CameraSource

NAME_MAX_LENGTH = 100
CODE_MAX_LENGTH = 30


@dataclass(slots=True)
class Camera:
    name: str
    code: str
    location_id: int
    source: CameraSource
    status: CameraStatus = CameraStatus.ACTIVE
    id: int | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    def __post_init__(self) -> None:
        self.name = _clean_text(self.name, "name", NAME_MAX_LENGTH)
        self.code = _clean_text(self.code, "code", CODE_MAX_LENGTH)
        self.location_id = _check_location(self.location_id)

    @classmethod
    def create(cls, *, name: str, code: str, location_id: int, source: CameraSource) -> Self:
        return cls(name=name, code=code, location_id=location_id, source=source)

    def update(self, *, name: str, code: str, location_id: int, source: CameraSource) -> None:
        # Se valida todo antes de asignar para no dejar la entidad a medio modificar.
        name = _clean_text(name, "name", NAME_MAX_LENGTH)
        code = _clean_text(code, "code", CODE_MAX_LENGTH)
        location_id = _check_location(location_id)

        self.name = name
        self.code = code
        self.location_id = location_id
        self.source = source

    def change_status(self, status: CameraStatus) -> None:
        self.status = status


def _clean_text(value: str, field: str, max_length: int) -> str:
    value = value.strip()
    if not value:
        raise InvalidCameraError(f"{field} es obligatorio")
    if len(value) > max_length:
        raise InvalidCameraError(f"{field} no puede superar {max_length} caracteres")
    return value


def _check_location(location_id: int) -> int:
    if location_id <= 0:
        raise InvalidCameraError("location_id debe ser un entero positivo")
    return location_id
