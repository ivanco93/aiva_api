from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from aiva.database.session import get_session
from aiva.database.sqlalchemy_transaction_manager import SqlAlchemyTransactionManager
from aiva.modules.camera.application.contracts.transaction_manager import TransactionManager
from aiva.modules.camera.application.use_cases.camera.change_camera_status import ChangeCameraStatusUseCase
from aiva.modules.camera.application.use_cases.camera.create_camera import CreateCameraUseCase
from aiva.modules.camera.application.use_cases.camera.delete_camera import DeleteCameraUseCase
from aiva.modules.camera.application.use_cases.camera.list_cameras import ListCamerasUseCase
from aiva.modules.camera.application.use_cases.camera.show_camera_by_id import ShowCameraByIdUseCase
from aiva.modules.camera.application.use_cases.camera.update_camera import UpdateCameraUseCase
from aiva.modules.camera.domain.repositories.camera_repository import CameraRepository
from aiva.modules.camera.infrastructure.persistence.sqlalchemy.repositories.sqlalchemy_camera_repository import (
    SqlAlchemyCameraRepository,
)

# FastAPI cachea las dependencias por request: repositorio y transaction manager comparten la misma sesión.
SessionDep = Annotated[AsyncSession, Depends(get_session)]


def get_camera_repository(session: SessionDep) -> CameraRepository:
    return SqlAlchemyCameraRepository(session)


def get_transaction_manager(session: SessionDep) -> TransactionManager:
    return SqlAlchemyTransactionManager(session)


RepositoryDep = Annotated[CameraRepository, Depends(get_camera_repository)]
TransactionDep = Annotated[TransactionManager, Depends(get_transaction_manager)]


def get_create_camera_use_case(repository: RepositoryDep, transaction: TransactionDep) -> CreateCameraUseCase:
    return CreateCameraUseCase(repository, transaction)


def get_show_camera_by_id_use_case(repository: RepositoryDep) -> ShowCameraByIdUseCase:
    return ShowCameraByIdUseCase(repository)


def get_list_cameras_use_case(repository: RepositoryDep) -> ListCamerasUseCase:
    return ListCamerasUseCase(repository)


def get_update_camera_use_case(repository: RepositoryDep, transaction: TransactionDep) -> UpdateCameraUseCase:
    return UpdateCameraUseCase(repository, transaction)


def get_change_camera_status_use_case(
    repository: RepositoryDep, transaction: TransactionDep
) -> ChangeCameraStatusUseCase:
    return ChangeCameraStatusUseCase(repository, transaction)


def get_delete_camera_use_case(repository: RepositoryDep, transaction: TransactionDep) -> DeleteCameraUseCase:
    return DeleteCameraUseCase(repository, transaction)
