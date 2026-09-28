from dataclasses import dataclass

from aiva.modules.camera.domain.enums.camera_source_type import CameraSourceType


@dataclass(frozen=True, slots=True)
class CreateCameraDTO:
    name: str
    code: str
    location_id: int
    source_type: CameraSourceType
    source_url: str
