from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "PocketSmart AI"
    debug: bool = True
    secret_key: str = "change-me"
    database_url: str = "sqlite:///./pocketsmart.db"
    gemini_api_key: str = ""
    gemini_model: str = "gemini-1.5-flash"
    access_token_expire_minutes: int = 1440
    host: str = "127.0.0.1"
    port: int = 8000
    frontend_origin: str = "http://127.0.0.1:8000"
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
