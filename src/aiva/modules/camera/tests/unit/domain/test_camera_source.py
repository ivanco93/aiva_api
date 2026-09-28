import pytest

from aiva.modules.camera.domain.enums.camera_source_type import CameraSourceType
from aiva.modules.camera.domain.exceptions.invalid_camera_error import InvalidCameraError
from aiva.modules.camera.domain.value_objects.camera_source import CameraSource


def test_accepts_url_matching_source_type():
    source = CameraSource(CameraSourceType.RTSP, "  rtsp://10.0.0.10:554/stream1  ")

    assert source.url == "rtsp://10.0.0.10:554/stream1"


def test_rejects_url_with_wrong_scheme():
    with pytest.raises(InvalidCameraError, match="rtsp://"):
        CameraSource(CameraSourceType.RTSP, "http://10.0.0.10/stream")


def test_rejects_empty_url():
    with pytest.raises(InvalidCameraError, match="obligatorio"):
        CameraSource(CameraSourceType.HTTP, "   ")


def test_file_source_accepts_local_paths():
    source = CameraSource(CameraSourceType.FILE, "C:/videos/entrada.mp4")

    assert source.url == "C:/videos/entrada.mp4"
