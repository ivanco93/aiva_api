from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from aiva.modules.camera.domain.entities.camera import Camera
from aiva.modules.camera.domain.enums.camera_source_type import CameraSourceType
from aiva.modules.camera.domain.enums.camera_status import CameraStatus
from aiva.modules.camera.domain.exceptions.camera_not_found_error import CameraNotFoundError
from aiva.modules.camera.infrastructure.persistence.sqlalchemy.mappers.camera_mapper import CameraMapper
from aiva.modules.camera.infrastructure.persistence.sqlalchemy.models.camera_model import CameraModel


class SqlAlchemyCameraRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def find_by_id(self, camera_id: int) -> Camera | None:
        model = await self._session.get(CameraModel, camera_id)
        return CameraMapper.to_entity(model) if model is not None else None

    async def find_by_code(self, code: str) -> Camera | None:
        model = await self._session.scalar(select(CameraModel).where(func.lower(CameraModel.code) == code.lower()))
        return CameraMapper.to_entity(model) if model is not None else None

    async def search(
        self,
        *,
        name: str | None = None,
        code: str | None = None,
        location_id: int | None = None,
        status: CameraStatus | None = None,
        source_type: CameraSourceType | None = None,
        offset: int = 0,
        limit: int = 20,
    ) -> tuple[list[Camera], int]:
        query = select(CameraModel)
        if name:
            query = query.where(CameraModel.name.icontains(name, autoescape=True))
        if code:
            query = query.where(func.lower(CameraModel.code) == code.lower())
        if location_id is not None:
            query = query.where(CameraModel.location_id == location_id)
        if status is not None:
            query = query.where(CameraModel.status == status.value)
        if source_type is not None:
            query = query.where(CameraModel.source_type == source_type.value)

        count = await self._session.scalar(select(func.count()).select_from(query.subquery())) or 0
        models = await self._session.scalars(query.order_by(CameraModel.id).offset(offset).limit(limit))
        return [CameraMapper.to_entity(model) for model in models], count

    async def save(self, camera: Camera) -> Camera:
        if camera.id is None:
            model = CameraModel()
            self._session.add(model)
        else:
            model = await self._session.get(CameraModel, camera.id)
            if model is None:
                raise CameraNotFoundError(camera.id)

        CameraMapper.apply_to_model(camera, model)
        await self._session.flush()
        # Trae id, created_at y updated_at generados por la base de datos.
        await self._session.refresh(model)
        return CameraMapper.to_entity(model)

    async def delete(self, camera_id: int) -> None:
        await self._session.execute(delete(CameraModel).where(CameraModel.id == camera_id))
