from aiva.modules.camera.domain.exceptions.camera_error import CameraError


class CameraCodeAlreadyExistsError(CameraError):
    def __init__(self, code: str) -> None:
        super().__init__(f"Ya existe una cámara con el código '{code}'")
        self.code = code
