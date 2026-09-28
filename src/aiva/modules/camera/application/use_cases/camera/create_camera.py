from aiva.modules.camera.application.builders.response.camera_response_builder import CameraResponseBuilder
from aiva.modules.camera.application.contracts.transaction_manager import TransactionManager
from aiva.modules.camera.application.dto.create_camera_dto import CreateCameraDTO
from aiva.modules.camera.application.dto.response.camera_response_dto import CameraResponseDTO
from aiva.modules.camera.domain.entities.camera import Camera
from aiva.modules.camera.domain.exceptions.camera_code_already_exists_error import CameraCodeAlreadyExistsError
from aiva.modules.camera.domain.repositories.camera_repository import CameraRepository
from aiva.modules.camera.domain.value_objects.camera_source import CameraSource


class CreateCameraUseCase:
    def __init__(self, repository: CameraRepository, transaction_manager: TransactionManager) -> None:
        self._repository = repository
        self._transaction_manager = transaction_manager

    async def execute(self, dto: CreateCameraDTO) -> CameraResponseDTO:
        camera = Camera.create(
            name=dto.name,
            code=dto.code,
            location_id=dto.location_id,
            source=CameraSource(dto.source_type, dto.source_url),
        )

        async with self._transaction_manager.transaction():
            if await self._repository.find_by_code(camera.code) is not None:
                raise CameraCodeAlreadyExistsError(camera.code)
            saved = await self._repository.save(camera)

        return CameraResponseBuilder.build(saved)
