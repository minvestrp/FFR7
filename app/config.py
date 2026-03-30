from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    APP_NAME: str = "SmartSec API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    DATABASE_URL: str = "postgresql+asyncpg://smartsec:smartsec@localhost:5432/smartsec"
    REDIS_URL: str = "redis://localhost:6379/0"

    SECRET_KEY: str = "change-me-in-production-use-strong-random-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24h

    ETHERSCAN_API_KEY: Optional[str] = None
    INFURA_PROJECT_ID: Optional[str] = None

    CORS_ORIGINS: list[str] = ["http://localhost:3000", "https://minvestrp.github.io"]

    class Config:
        env_file = ".env"

settings = Settings()
