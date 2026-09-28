from datetime import datetime

from sqlalchemy import FetchedValue, String, func
from sqlalchemy.orm import Mapped, mapped_column

from aiva.database.base import Base


class CameraModel(Base):
    __tablename__ = "cameras"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100))
    code: Mapped[str] = mapped_column(String(30), unique=True)
    location_id: Mapped[int]
    source_type: Mapped[str] = mapped_column(String(20))
    source_url: Mapped[str] = mapped_column(String(2048))
    status: Mapped[str] = mapped_column(String(20), server_default="active")
    created_at: Mapped[datetime] = mapped_column(server_default=func.current_timestamp())
    # MySQL la actualiza con ON UPDATE CURRENT_TIMESTAMP; se relee tras cada flush.
    updated_at: Mapped[datetime | None] = mapped_column(server_onupdate=FetchedValue())
