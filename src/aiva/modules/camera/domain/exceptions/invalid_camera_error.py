from aiva.modules.camera.domain.exceptions.camera_error import CameraError


class InvalidCameraError(CameraError):
    """Se lanza cuando un dato de la cámara rompe una regla de negocio."""
