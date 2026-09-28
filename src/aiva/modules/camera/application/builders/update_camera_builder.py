from collections.abc import Mapping
from typing import Any

from aiva.modules.camera.application.dto.update_camera_dto import UpdateCameraDTO
from aiva.modules.camera.domain.enums.camera_source_type import CameraSourceType


class UpdateCameraBuilder:
    @staticmethod
    def build(camera_id: int, data: Mapping[str, Any]) -> UpdateCameraDTO:
        return UpdateCameraDTO(
            camera_id=camera_id,
            name=data["name"],
            code=data["code"],
            location_id=int(data["location_id"]),
            source_type=CameraSourceType(data["source_type"]),
            source_url=data["source_url"],
        )
