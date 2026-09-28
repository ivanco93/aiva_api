from collections.abc import Mapping
from typing import Any

from aiva.modules.camera.application.dto.list_cameras_query_dto import ListCamerasQueryDTO
from aiva.modules.camera.domain.enums.camera_source_type import CameraSourceType
from aiva.modules.camera.domain.enums.camera_status import CameraStatus


class ListCamerasQueryBuilder:
    @staticmethod
    def build(data: Mapping[str, Any]) -> ListCamerasQueryDTO:
        status = data.get("status")
        source_type = data.get("source_type")
        return ListCamerasQueryDTO(
            name=data.get("name") or None,
            code=data.get("code") or None,
            location_id=data.get("location_id"),
            status=CameraStatus(status) if status else None,
            source_type=CameraSourceType(source_type) if source_type else None,
            offset=data.get("offset") or 0,
            limit=data.get("limit") or 20,
        )
