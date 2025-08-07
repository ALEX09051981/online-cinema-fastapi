from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )

    DATABASE_URL: str
    MAILGUN_API_KEY: str
    MAILGUN_DOMAIN: str
    BASE_URL: str = "http://localhost:8000"
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"

settings = Settings()
