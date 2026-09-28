from aiva.modules.camera.application.builders.response.camera_response_builder import CameraResponseBuilder
from aiva.modules.camera.application.dto.list_cameras_query_dto import ListCamerasQueryDTO
from aiva.modules.camera.application.dto.response.camera_list_response_dto import CameraListResponseDTO
from aiva.modules.camera.domain.repositories.camera_repository import CameraRepository


class ListCamerasUseCase:
    def __init__(self, repository: CameraRepository) -> None:
        self._repository = repository

    async def execute(self, dto: ListCamerasQueryDTO) -> CameraListResponseDTO:
        cameras, count = await self._repository.search(
            name=dto.name,
            code=dto.code,
            location_id=dto.location_id,
            status=dto.status,
            source_type=dto.source_type,
            offset=dto.offset,
            limit=dto.limit,
        )
        return CameraResponseBuilder.build_list(cameras, count)
