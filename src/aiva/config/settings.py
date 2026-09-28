from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Obligatoria: la app no arranca sin ella. Ej: mysql+aiomysql://user:pass@127.0.0.1:3306/aiva
    database_url: str
    database_echo: bool = False


@lru_cache
def get_settings() -> Settings:
    return Settings()
