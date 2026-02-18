from pydantic_settings import BaseSettings, SettingsConfigDict

_base_config = SettingsConfigDict(
    env_file=".env",
    extra="ignore",
    env_ignore_empty=True,
)


class Configs(BaseSettings):
    # App settings
    APP_NAME: str = "Ghost2Lead"
    DEBUG: bool = False
    API_PREFIX: str = "/api"
    API_V1: str = "/api/v1"

    # Database settings
    DATABASE_USER: str
    DATABASE_PASSWORD: str
    DATABASE_SERVER: str
    DATABASE_PORT: int = 5432
    DATABASE_NAME: str

    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql+asyncpg://{self.DATABASE_USER}:{self.DATABASE_PASSWORD}@{self.DATABASE_SERVER}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"

    model_config = _base_config

    # IP encryption key
    IP_ENCRYPTION_KEY: str
    
    # CORS settings
    BACKEND_CORS_ORIGINS: list[str] | None = None


configs = Configs()
