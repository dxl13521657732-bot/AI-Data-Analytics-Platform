from typing import List, Union
from pydantic import field_validator
from pydantic_settings import BaseSettings


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

    # 支持逗号分隔字符串或 JSON 数组
    cors_origins: List[str] = ["http://localhost:5173", "http://localhost:80"]

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            # 支持逗号分隔格式：http://a.com,http://b.com
            return [x.strip() for x in v.split(",") if x.strip()]
        return v

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
