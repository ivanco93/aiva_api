from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from aiva.modules.camera.application.builders.change_camera_status_builder import ChangeCameraStatusBuilder
from aiva.modules.camera.application.builders.create_camera_builder import CreateCameraBuilder
from aiva.modules.camera.application.builders.list_cameras_query_builder import ListCamerasQueryBuilder
from aiva.modules.camera.application.builders.update_camera_builder import UpdateCameraBuilder
from aiva.modules.camera.application.use_cases.camera.change_camera_status import ChangeCameraStatusUseCase
from aiva.modules.camera.application.use_cases.camera.create_camera import CreateCameraUseCase
from aiva.modules.camera.application.use_cases.camera.delete_camera import DeleteCameraUseCase
from aiva.modules.camera.application.use_cases.camera.list_cameras import ListCamerasUseCase
from aiva.modules.camera.application.use_cases.camera.show_camera_by_id import ShowCameraByIdUseCase
from aiva.modules.camera.application.use_cases.camera.update_camera import UpdateCameraUseCase
from aiva.modules.camera.infrastructure.http.dependencies import (
    get_change_camera_status_use_case,
    get_create_camera_use_case,
    get_delete_camera_use_case,
    get_list_cameras_use_case,
    get_show_camera_by_id_use_case,
    get_update_camera_use_case,
)
from aiva.modules.camera.infrastructure.http.schemas.camera_response import CameraListResponse, CameraResponse
from aiva.modules.camera.infrastructure.http.schemas.change_camera_status_request import ChangeCameraStatusRequest
from aiva.modules.camera.infrastructure.http.schemas.create_camera_request import CreateCameraRequest
from aiva.modules.camera.infrastructure.http.schemas.list_cameras_request import ListCamerasRequest
from aiva.modules.camera.infrastructure.http.schemas.update_camera_request import UpdateCameraRequest

router = APIRouter(prefix="/cameras", tags=["camera"])

# ":int" evita que futuras rutas fijas (ej. /cameras/stats) se confundan con /cameras/{camera_id}.
CAMERA_PATH = "/{camera_id:int}"


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_camera(
    body: CreateCameraRequest,
    use_case: Annotated[CreateCameraUseCase, Depends(get_create_camera_use_case)],
) -> CameraResponse:
    result = await use_case.execute(CreateCameraBuilder.build(body.model_dump()))
    return CameraResponse.model_validate(result)


@router.get("")
async def list_cameras(
    query: Annotated[ListCamerasRequest, Query()],
    use_case: Annotated[ListCamerasUseCase, Depends(get_list_cameras_use_case)],
) -> CameraListResponse:
    result = await use_case.execute(ListCamerasQueryBuilder.build(query.model_dump()))
    return CameraListResponse.model_validate(result)


@router.get(CAMERA_PATH)
async def show_camera(
    camera_id: int,
    use_case: Annotated[ShowCameraByIdUseCase, Depends(get_show_camera_by_id_use_case)],
) -> CameraResponse:
    result = await use_case.execute(camera_id)
    return CameraResponse.model_validate(result)


@router.put(CAMERA_PATH)
async def update_camera(
    camera_id: int,
    body: UpdateCameraRequest,
    use_case: Annotated[UpdateCameraUseCase, Depends(get_update_camera_use_case)],
) -> CameraResponse:
    result = await use_case.execute(UpdateCameraBuilder.build(camera_id, body.model_dump()))
    return CameraResponse.model_validate(result)


@router.put(CAMERA_PATH + "/status")
async def change_camera_status(
    camera_id: int,
    body: ChangeCameraStatusRequest,
    use_case: Annotated[ChangeCameraStatusUseCase, Depends(get_change_camera_status_use_case)],
) -> CameraResponse:
    result = await use_case.execute(ChangeCameraStatusBuilder.build(camera_id, body.model_dump()))
    return CameraResponse.model_validate(result)


@router.delete(CAMERA_PATH, status_code=status.HTTP_204_NO_CONTENT)
async def delete_camera(
    camera_id: int,
    use_case: Annotated[DeleteCameraUseCase, Depends(get_delete_camera_use_case)],
) -> None:
    await use_case.execute(camera_id)
