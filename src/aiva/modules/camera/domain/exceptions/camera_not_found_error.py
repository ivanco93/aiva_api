from aiva.modules.camera.domain.exceptions.camera_error import CameraError


class CameraNotFoundError(CameraError):
    def __init__(self, camera_id: int) -> None:
        super().__init__(f"No existe la cámara con id {camera_id}")
        self.camera_id = camera_id
