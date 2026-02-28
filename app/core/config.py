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

    # PostHog
    POSTHOG_DATABASE_URL: str
    POSTHOG_PROJECT_ID: int
    POSTHOG_EVENTS_TABLE_NAME: str
    
    # OpenAI
    OPENAI_API_KEY: str

    # CORS settings
    BACKEND_CORS_ORIGINS: list[str] | None = None

    # Pagination settings
    PAGE: int = 1
    PAGE_SIZE: int = 10
    PAGE_SIZE_MIN: int = 1
    PAGE_SIZE_MAX: int = 100

    # JWT / Auth settings
    JWT_SECRET: str = "change-me-in-production"
    JWT_ALGO: str = "HS256"
    JWT_EXPIRE_DAYS: int = 7

    # Redis (required for OTP auth, token blacklist, Celery)
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB_OTP: int = 1
    REDIS_DB_TOKEN_BLACKLIST: int = 2
    REDIS_DB_CELERY: int = 0

    # OTP settings
    OTP_TTL_SECONDS: int = 600  # 10 minutes
    OTP_LENGTH: int = 6


    # Mail (for OTP and notifications)
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: str = "noreply@example.com"
    MAIL_FROM_NAME: str = APP_NAME
    MAIL_SERVER: str = "smtp.gmail.com"
    MAIL_PORT: int = 587
    MAIL_STARTTLS: bool = True
    MAIL_SSL_TLS: bool = False
    TEMPLATE_DIR: str = "template"

    def redis_url(self, db: int) -> str:
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{db}"


configs = Configs()
