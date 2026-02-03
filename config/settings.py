from pydantic_settings import BaseSettings, SettingsConfigDict

_base_config = SettingsConfigDict(
    env_file=".env",
    extra="ignore",
    env_ignore_empty=True,
)


class AppSettings(BaseSettings):
    APP_NAME: str = "Ghost2Lead"
    DEBUG: bool = False
    API_PREFIX: str = "/api"
    API_VERSION: str = "v1"

    model_config = _base_config


settings = AppSettings()
