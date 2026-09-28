from aiva.modules.camera.application.dto.response.camera_list_response_dto import CameraListResponseDTO
from aiva.modules.camera.application.dto.response.camera_response_dto import CameraResponseDTO
from aiva.modules.camera.domain.entities.camera import Camera


class CameraResponseBuilder:
    @staticmethod
    def build(camera: Camera) -> CameraResponseDTO:
        if camera.id is None:
            raise ValueError("No se puede construir la respuesta de una cámara sin persistir")
        return CameraResponseDTO(
            id=camera.id,
            name=camera.name,
            code=camera.code,
            location_id=camera.location_id,
            source_type=camera.source.source_type.value,
            source_url=camera.source.url,
            status=camera.status.value,
            created_at=camera.created_at,
            updated_at=camera.updated_at,
        )

    @staticmethod
    def build_list(cameras: list[Camera], count: int) -> CameraListResponseDTO:
        return CameraListResponseDTO(data=[CameraResponseBuilder.build(c) for c in cameras], count=count)
