from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    app_secret_key: str = "dev-secret-key-change-in-production"
    app_access_token_expire_minutes: int = 480

    anthropic_api_key: str = ""
    anthropic_model: str = "claude-sonnet-4-5"
    anthropic_max_tokens: int = 4096

    starrocks_host: str = "localhost"
    starrocks_port: int = 9030
    starrocks_user: str = "root"
    starrocks_password: str = ""
    starrocks_read_timeout: int = 30

    tdata_api_base: str = ""
    tdata_api_token: str = ""

    sqlite_path: str = "./data/platform.db"

    cors_origins: List[str] = ["http://localhost:5173", "http://localhost:80"]

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
