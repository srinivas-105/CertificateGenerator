from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Certificate Generation API"
    api_v1_prefix: str = "/api/v1"
    database_url: str = "sqlite:///./certificate_generator.db"
    max_recipients_per_job: int = 1000
    output_directory: str = "generated_certificates"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
