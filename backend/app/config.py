from functools import lru_cache
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str = "sqlite:///./app.db"
    secret_key: str = "CHANGE_ME"
    tasty_refresh_token: str | None = None
    tasty_base_url: str = "https://api.tastytrade.com"
    tasty_client_id: str | None = None
    tasty_client_secret: str | None = None

    class Config:
        env_file = ".env"

@lru_cache
def get_settings() -> Settings:
    return Settings()
