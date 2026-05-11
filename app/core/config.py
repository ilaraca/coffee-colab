from typing import Optional
from pydantic import ConfigDict
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    model_config = ConfigDict(env_file=".env")

    # Padrão alinhado ao docker-compose.yml (host 5433 -> container 5432)
    DATABASE_URL: str = "postgresql://user:password@localhost:5433/modocolab"
    SECRET_KEY: str = "dev_secret"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    SENTRY_DSN: Optional[str] = None

    # Email / SMTP (optional — if not set, links are logged to console)
    MAIL_USERNAME: Optional[str] = None
    MAIL_PASSWORD: Optional[str] = None
    MAIL_FROM: str = "noreply@modocolab.com"
    MAIL_SERVER: str = "sandbox.smtp.mailtrap.io"
    MAIL_PORT: int = 587
    MAIL_STARTTLS: bool = True  # False para servidor SMTP local sem TLS (ex.: testes)

    # Base URL used in verification links
    APP_BASE_URL: str = "http://localhost:8000"

settings = Settings()
