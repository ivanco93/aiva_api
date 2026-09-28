from aiva.modules.camera.application.builders.response.camera_response_builder import CameraResponseBuilder
from aiva.modules.camera.application.dto.response.camera_response_dto import CameraResponseDTO
from aiva.modules.camera.domain.exceptions.camera_not_found_error import CameraNotFoundError
from aiva.modules.camera.domain.repositories.camera_repository import CameraRepository


class ShowCameraByIdUseCase:
    def __init__(self, repository: CameraRepository) -> None:
        self._repository = repository

    async def execute(self, camera_id: int) -> CameraResponseDTO:
        camera = await self._repository.find_by_id(camera_id)
        if camera is None:
            raise CameraNotFoundError(camera_id)
        return CameraResponseBuilder.build(camera)
