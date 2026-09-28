from datetime import datetime

from pydantic import BaseModel, ConfigDict


class CameraResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    code: str
    location_id: int
    source_type: str
    source_url: str
    status: str
    created_at: datetime | None
    updated_at: datetime | None


class CameraListResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    data: list[CameraResponse]
    count: int
