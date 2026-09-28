from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from aiva.modules.camera.domain.exceptions.camera_code_already_exists_error import CameraCodeAlreadyExistsError
from aiva.modules.camera.domain.exceptions.camera_error import CameraError
from aiva.modules.camera.domain.exceptions.camera_not_found_error import CameraNotFoundError
from aiva.modules.camera.domain.exceptions.invalid_camera_error import InvalidCameraError

_STATUS_BY_ERROR: dict[type[CameraError], int] = {
    CameraNotFoundError: status.HTTP_404_NOT_FOUND,
    CameraCodeAlreadyExistsError: status.HTTP_409_CONFLICT,
    InvalidCameraError: status.HTTP_422_UNPROCESSABLE_CONTENT,
}


async def camera_error_handler(_: Request, exc: Exception) -> JSONResponse:
    status_code = next(
        (code for error, code in _STATUS_BY_ERROR.items() if isinstance(exc, error)),
        status.HTTP_400_BAD_REQUEST,
    )
    return JSONResponse(status_code=status_code, content={"detail": str(exc)})


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(CameraError, camera_error_handler)
