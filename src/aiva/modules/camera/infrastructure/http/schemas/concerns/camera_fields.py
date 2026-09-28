from pydantic import BaseModel, ConfigDict, Field

from aiva.modules.camera.domain.enums.camera_source_type import CameraSourceType


class CameraFields(BaseModel):
    """Campos comunes del body de creación y actualización."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    name: str = Field(min_length=1, max_length=100, examples=["Entrada principal"])
    code: str = Field(min_length=1, max_length=30, examples=["CAM-001"])
    location_id: int = Field(gt=0, examples=[1])
    source_type: CameraSourceType
    source_url: str = Field(min_length=1, max_length=2048, examples=["rtsp://10.0.0.10:554/stream1"])
