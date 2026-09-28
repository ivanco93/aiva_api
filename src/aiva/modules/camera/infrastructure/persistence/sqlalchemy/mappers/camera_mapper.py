from aiva.modules.camera.domain.entities.camera import Camera
from aiva.modules.camera.domain.enums.camera_source_type import CameraSourceType
from aiva.modules.camera.domain.enums.camera_status import CameraStatus
from aiva.modules.camera.domain.value_objects.camera_source import CameraSource
from aiva.modules.camera.infrastructure.persistence.sqlalchemy.models.camera_model import CameraModel


class CameraMapper:
    @staticmethod
    def to_entity(model: CameraModel) -> Camera:
        return Camera(
            id=model.id,
            name=model.name,
            code=model.code,
            location_id=model.location_id,
            source=CameraSource(CameraSourceType(model.source_type), model.source_url),
            status=CameraStatus(model.status),
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @staticmethod
    def apply_to_model(camera: Camera, model: CameraModel) -> None:
        model.name = camera.name
        model.code = camera.code
        model.location_id = camera.location_id
        model.source_type = camera.source.source_type.value
        model.source_url = camera.source.url
        model.status = camera.status.value
