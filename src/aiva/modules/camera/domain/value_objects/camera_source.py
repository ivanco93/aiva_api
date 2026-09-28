from dataclasses import dataclass

from aiva.modules.camera.domain.enums.camera_source_type import CameraSourceType
from aiva.modules.camera.domain.exceptions.invalid_camera_error import InvalidCameraError

SOURCE_URL_MAX_LENGTH = 2048

# Esquemas de URL aceptados por cada tipo de fuente. FILE no se restringe (rutas locales).
_ALLOWED_SCHEMES: dict[CameraSourceType, tuple[str, ...]] = {
    CameraSourceType.RTSP: ("rtsp://", "rtsps://"),
    CameraSourceType.RTMP: ("rtmp://", "rtmps://"),
    CameraSourceType.HTTP: ("http://", "https://"),
    CameraSourceType.HLS: ("http://", "https://"),
}


@dataclass(frozen=True, slots=True)
class CameraSource:
    """Par tipo + URL de la fuente de video. Solo existe si es coherente."""

    source_type: CameraSourceType
    url: str

    def __post_init__(self) -> None:
        url = self.url.strip()
        if not url:
            raise InvalidCameraError("source_url es obligatorio")
        if len(url) > SOURCE_URL_MAX_LENGTH:
            raise InvalidCameraError(f"source_url no puede superar {SOURCE_URL_MAX_LENGTH} caracteres")

        schemes = _ALLOWED_SCHEMES.get(self.source_type)
        if schemes and not url.lower().startswith(schemes):
            raise InvalidCameraError(
                f"source_url debe empezar por {' o '.join(schemes)} cuando source_type es '{self.source_type}'"
            )

        object.__setattr__(self, "url", url)
