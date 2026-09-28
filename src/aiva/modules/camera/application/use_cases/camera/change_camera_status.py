from aiva.modules.camera.application.builders.response.camera_response_builder import CameraResponseBuilder
from aiva.modules.camera.application.contracts.transaction_manager import TransactionManager
from aiva.modules.camera.application.dto.change_camera_status_dto import ChangeCameraStatusDTO
from aiva.modules.camera.application.dto.response.camera_response_dto import CameraResponseDTO
from aiva.modules.camera.domain.exceptions.camera_not_found_error import CameraNotFoundError
from aiva.modules.camera.domain.repositories.camera_repository import CameraRepository


class ChangeCameraStatusUseCase:
    def __init__(self, repository: CameraRepository, transaction_manager: TransactionManager) -> None:
        self._repository = repository
        self._transaction_manager = transaction_manager

    async def execute(self, dto: ChangeCameraStatusDTO) -> CameraResponseDTO:
        async with self._transaction_manager.transaction():
            camera = await self._repository.find_by_id(dto.camera_id)
            if camera is None:
                raise CameraNotFoundError(dto.camera_id)

            camera.change_status(dto.status)
            saved = await self._repository.save(camera)

        return CameraResponseBuilder.build(saved)
