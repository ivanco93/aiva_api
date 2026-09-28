from pydantic import BaseModel, ConfigDict, Field

from aiva.modules.camera.domain.enums.camera_source_type import CameraSourceType
from aiva.modules.camera.domain.enums.camera_status import CameraStatus


class ListCamerasRequest(BaseModel):
    """Query params de GET /cameras; solo se envían los filtros que se usan."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    name: str | None = Field(default=None, max_length=100, description="Búsqueda parcial por nombre")
    code: str | None = Field(default=None, max_length=30)
    location_id: int | None = Field(default=None, gt=0)
    status: CameraStatus | None = None
    source_type: CameraSourceType | None = None
    offset: int = Field(default=0, ge=0)
    limit: int = Field(default=20, ge=1, le=100)
