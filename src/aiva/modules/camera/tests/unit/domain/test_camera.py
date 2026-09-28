import pytest

from aiva.modules.camera.domain.entities.camera import Camera
from aiva.modules.camera.domain.enums.camera_source_type import CameraSourceType
from aiva.modules.camera.domain.enums.camera_status import CameraStatus
from aiva.modules.camera.domain.exceptions.invalid_camera_error import InvalidCameraError
from aiva.modules.camera.domain.value_objects.camera_source import CameraSource

SOURCE = CameraSource(CameraSourceType.RTSP, "rtsp://10.0.0.10/stream1")


def make_camera() -> Camera:
    return Camera.create(name="Entrada principal", code="CAM-001", location_id=1, source=SOURCE)


def test_create_starts_active_and_strips_text():
    camera = Camera.create(name="  Entrada  ", code=" CAM-001 ", location_id=1, source=SOURCE)

    assert camera.status is CameraStatus.ACTIVE
    assert camera.name == "Entrada"
    assert camera.code == "CAM-001"
    assert camera.id is None


@pytest.mark.parametrize(
    ("name", "code", "location_id", "message"),
    [
        ("", "CAM-001", 1, "name"),
        ("Entrada", "", 1, "code"),
        ("x" * 101, "CAM-001", 1, "name"),
        ("Entrada", "CAM-001", 0, "location_id"),
    ],
)
def test_create_rejects_invalid_data(name, code, location_id, message):
    with pytest.raises(InvalidCameraError, match=message):
        Camera.create(name=name, code=code, location_id=location_id, source=SOURCE)


def test_update_is_atomic_when_validation_fails():
    camera = make_camera()

    with pytest.raises(InvalidCameraError):
        camera.update(name="Nuevo nombre", code="CAM-002", location_id=-1, source=SOURCE)

    assert camera.name == "Entrada principal"
    assert camera.code == "CAM-001"


def test_change_status():
    camera = make_camera()

    camera.change_status(CameraStatus.MAINTENANCE)

    assert camera.status is CameraStatus.MAINTENANCE
