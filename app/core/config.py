from pydantic_settings import BaseSettings, SettingsConfigDict
import os


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    DATABASE_URL: str
    MAILGUN_API_KEY: str
    MAILGUN_DOMAIN: str
    BASE_URL: str = "http://localhost:8000"

settings = Settings()
