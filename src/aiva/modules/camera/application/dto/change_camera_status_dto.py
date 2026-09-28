from dataclasses import dataclass

from aiva.modules.camera.domain.enums.camera_status import CameraStatus


@dataclass(frozen=True, slots=True)
class ChangeCameraStatusDTO:
    camera_id: int
    status: CameraStatus
