from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class CameraResponseDTO:
    id: int
    name: str
    code: str
    location_id: int
    source_type: str
    source_url: str
    status: str
    created_at: datetime | None
    updated_at: datetime | None
