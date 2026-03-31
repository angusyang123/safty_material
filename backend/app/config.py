from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    # 数据目录
    DATA_DIR: str = str(Path(__file__).parent.parent.parent / "data")

    # 服务器配置
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000

    # CORS配置
    CORS_ORIGINS: list = ["http://localhost:5173", "http://localhost:3000"]

    class Config:
        env_file = ".env"


settings = Settings()
