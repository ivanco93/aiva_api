from dataclasses import dataclass

from aiva.modules.camera.application.dto.response.camera_response_dto import CameraResponseDTO


@dataclass(frozen=True, slots=True)
class CameraListResponseDTO:
    data: list[CameraResponseDTO]
    count: int
