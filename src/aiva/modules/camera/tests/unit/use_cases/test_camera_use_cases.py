import pytest

from aiva.modules.camera.application.dto.change_camera_status_dto import ChangeCameraStatusDTO
from aiva.modules.camera.application.dto.create_camera_dto import CreateCameraDTO
from aiva.modules.camera.application.dto.list_cameras_query_dto import ListCamerasQueryDTO
from aiva.modules.camera.application.dto.update_camera_dto import UpdateCameraDTO
from aiva.modules.camera.application.use_cases.camera.change_camera_status import ChangeCameraStatusUseCase
from aiva.modules.camera.application.use_cases.camera.create_camera import CreateCameraUseCase
from aiva.modules.camera.application.use_cases.camera.delete_camera import DeleteCameraUseCase
from aiva.modules.camera.application.use_cases.camera.list_cameras import ListCamerasUseCase
from aiva.modules.camera.application.use_cases.camera.show_camera_by_id import ShowCameraByIdUseCase
from aiva.modules.camera.application.use_cases.camera.update_camera import UpdateCameraUseCase
from aiva.modules.camera.domain.enums.camera_source_type import CameraSourceType
from aiva.modules.camera.domain.enums.camera_status import CameraStatus
from aiva.modules.camera.domain.exceptions.camera_code_already_exists_error import CameraCodeAlreadyExistsError
from aiva.modules.camera.domain.exceptions.camera_not_found_error import CameraNotFoundError
from aiva.modules.camera.tests.fakes import InMemoryCameraRepository
from aiva.testing.transaction_manager_stub import TransactionManagerStub

pytestmark = pytest.mark.anyio


def create_dto(code: str = "CAM-001", location_id: int = 1) -> CreateCameraDTO:
    return CreateCameraDTO(
        name="Entrada principal",
        code=code,
        location_id=location_id,
        source_type=CameraSourceType.RTSP,
        source_url="rtsp://10.0.0.10/stream1",
    )


async def test_create_returns_persisted_camera():
    repository, tx = InMemoryCameraRepository(), TransactionManagerStub()

    result = await CreateCameraUseCase(repository, tx).execute(create_dto())

    assert result.id == 1
    assert result.code == "CAM-001"
    assert result.status == "active"
    assert result.source_type == "rtsp"
    assert tx.commits == 1


async def test_create_rejects_duplicated_code():
    repository, tx = InMemoryCameraRepository(), TransactionManagerStub()
    use_case = CreateCameraUseCase(repository, tx)
    await use_case.execute(create_dto())

    with pytest.raises(CameraCodeAlreadyExistsError):
        await use_case.execute(create_dto())

    assert tx.rollbacks == 1


async def test_show_raises_when_camera_does_not_exist():
    with pytest.raises(CameraNotFoundError):
        await ShowCameraByIdUseCase(InMemoryCameraRepository()).execute(99)


async def test_update_changes_fields():
    repository, tx = InMemoryCameraRepository(), TransactionManagerStub()
    created = await CreateCameraUseCase(repository, tx).execute(create_dto())

    result = await UpdateCameraUseCase(repository, tx).execute(
        UpdateCameraDTO(
            camera_id=created.id,
            name="Parqueadero",
            code="CAM-001",
            location_id=2,
            source_type=CameraSourceType.HLS,
            source_url="https://cdn.local/parqueadero.m3u8",
        )
    )

    assert result.name == "Parqueadero"
    assert result.location_id == 2
    assert result.source_type == "hls"


async def test_update_rejects_code_used_by_another_camera():
    repository, tx = InMemoryCameraRepository(), TransactionManagerStub()
    create = CreateCameraUseCase(repository, tx)
    await create.execute(create_dto(code="CAM-001"))
    second = await create.execute(create_dto(code="CAM-002"))

    with pytest.raises(CameraCodeAlreadyExistsError):
        await UpdateCameraUseCase(repository, tx).execute(
            UpdateCameraDTO(
                camera_id=second.id,
                name="Otra",
                code="CAM-001",
                location_id=1,
                source_type=CameraSourceType.RTSP,
                source_url="rtsp://10.0.0.11/stream1",
            )
        )

    unchanged = await ShowCameraByIdUseCase(repository).execute(second.id)
    assert unchanged.code == "CAM-002"


async def test_change_status():
    repository, tx = InMemoryCameraRepository(), TransactionManagerStub()
    created = await CreateCameraUseCase(repository, tx).execute(create_dto())

    result = await ChangeCameraStatusUseCase(repository, tx).execute(
        ChangeCameraStatusDTO(camera_id=created.id, status=CameraStatus.INACTIVE)
    )

    assert result.status == "inactive"


async def test_list_filters_and_paginates():
    repository, tx = InMemoryCameraRepository(), TransactionManagerStub()
    create = CreateCameraUseCase(repository, tx)
    for index in range(1, 4):
        await create.execute(create_dto(code=f"CAM-00{index}", location_id=1))
    await create.execute(create_dto(code="CAM-100", location_id=2))

    result = await ListCamerasUseCase(repository).execute(ListCamerasQueryDTO(location_id=1, offset=1, limit=1))

    assert result.count == 3
    assert [camera.code for camera in result.data] == ["CAM-002"]


async def test_delete_removes_camera():
    repository, tx = InMemoryCameraRepository(), TransactionManagerStub()
    created = await CreateCameraUseCase(repository, tx).execute(create_dto())

    await DeleteCameraUseCase(repository, tx).execute(created.id)

    with pytest.raises(CameraNotFoundError):
        await ShowCameraByIdUseCase(repository).execute(created.id)


async def test_delete_raises_when_camera_does_not_exist():
    with pytest.raises(CameraNotFoundError):
        await DeleteCameraUseCase(InMemoryCameraRepository(), TransactionManagerStub()).execute(99)
