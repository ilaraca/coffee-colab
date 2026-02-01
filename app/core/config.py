import os
from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/coffeecolab")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev_secret")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    SENTRY_DSN: Optional[str] = None

    class Config:
        env_file = ".env"

settings = Settings()
