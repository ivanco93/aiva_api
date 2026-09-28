from pydantic import BaseModel, ConfigDict

from aiva.modules.camera.domain.enums.camera_status import CameraStatus


class ChangeCameraStatusRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: CameraStatus
