from collections.abc import Mapping
from typing import Any

from aiva.modules.camera.application.dto.create_camera_dto import CreateCameraDTO
from aiva.modules.camera.domain.enums.camera_source_type import CameraSourceType


class CreateCameraBuilder:
    @staticmethod
    def build(data: Mapping[str, Any]) -> CreateCameraDTO:
        return CreateCameraDTO(
            name=data["name"],
            code=data["code"],
            location_id=int(data["location_id"]),
            source_type=CameraSourceType(data["source_type"]),
            source_url=data["source_url"],
        )
