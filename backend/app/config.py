"""
ZeeK.Web — Application Configuration
"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    APP_NAME: str = "ZeeK.Web"
    DEBUG: bool = True
    SECRET_KEY: str = "change...n"
    DATABASE_URL: str = "sqlite+aiosqlite:///./data/zeek.db"
    REDIS_URL: str = "redis://localhost:6379"
    DERIV_APP_ID: int = 24332
    DERIV_WS_URL: str = "wss://ws.derivws.com/websockets/v3"
    DERIV_API_URL: str = "https://api.derivws.com"
    MONITOR_URL: str = "http://79.143.190.252:8765/api/v1"
    MONITOR_ENABLED: bool = False
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"

    @property
    def CORS_ORIGINS_LIST(self) -> List[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",")]

    class Config:
        env_file = "../.env"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()
