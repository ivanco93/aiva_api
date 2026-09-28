from dataclasses import dataclass

from aiva.modules.camera.domain.enums.camera_source_type import CameraSourceType
from aiva.modules.camera.domain.enums.camera_status import CameraStatus


@dataclass(frozen=True, slots=True)
class ListCamerasQueryDTO:
    name: str | None = None
    code: str | None = None
    location_id: int | None = None
    status: CameraStatus | None = None
    source_type: CameraSourceType | None = None
    offset: int = 0
    limit: int = 20
