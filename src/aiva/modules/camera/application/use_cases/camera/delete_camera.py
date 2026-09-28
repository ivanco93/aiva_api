from aiva.modules.camera.application.contracts.transaction_manager import TransactionManager
from aiva.modules.camera.domain.exceptions.camera_not_found_error import CameraNotFoundError
from aiva.modules.camera.domain.repositories.camera_repository import CameraRepository


class DeleteCameraUseCase:
    def __init__(self, repository: CameraRepository, transaction_manager: TransactionManager) -> None:
        self._repository = repository
        self._transaction_manager = transaction_manager

    async def execute(self, camera_id: int) -> None:
        async with self._transaction_manager.transaction():
            if await self._repository.find_by_id(camera_id) is None:
                raise CameraNotFoundError(camera_id)
            await self._repository.delete(camera_id)
