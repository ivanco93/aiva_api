from collections.abc import Mapping
from typing import Any

from aiva.modules.camera.application.dto.change_camera_status_dto import ChangeCameraStatusDTO
from aiva.modules.camera.domain.enums.camera_status import CameraStatus


class ChangeCameraStatusBuilder:
    @staticmethod
    def build(camera_id: int, data: Mapping[str, Any]) -> ChangeCameraStatusDTO:
        return ChangeCameraStatusDTO(camera_id=camera_id, status=CameraStatus(data["status"]))
