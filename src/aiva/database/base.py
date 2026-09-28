from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base declarativa común a los modelos de todos los módulos. El esquema lo gestiona Flyway."""
