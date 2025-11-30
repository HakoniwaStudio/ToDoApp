from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """アプリケーション設定"""
    
    # アプリケーション設定
    APP_NAME: str = "ToDoApp"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True
    
    # データベース設定
    DATABASE_URL: str = "sqlite:///./todoapp.db"
    
    # API設定
    API_PREFIX: str = "/api/v1"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
