from pydantic_settings import BaseSettings
from typing import Optional
from pathlib import Path
import os

# backend/ 폴더에서 실행되므로 부모 디렉터리의 .env를 가리킴
_ENV_FILE = Path(__file__).parent.parent.parent / ".env"

class Settings(BaseSettings):
    database_url: str = "sqlite:///./fishingdaily.db"
    secret_key: str = "fishing-daily-secret-key"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    refresh_token_expire_days: int = 30

    openweather_api_key: str = ""
    kma_api_key: str = ""
    khoa_api_key: str = ""

    kakao_rest_api_key: str = ""
    kakao_redirect_uri: str = ""
    kakao_bizmessage_sender_key: str = ""
    kakao_template_id: str = ""

    gemini_api_key: str = ""
    gemini_model: str = "gemini-1.5-flash"

    llm_provider: str = "polaris"
    polaris_api_url: str = ""
    polaris_api_key: str = ""
    polaris_model: str = "polaris-chat"
    openai_api_key: str = ""
    openai_model: str = "gpt-4o"
    anthropic_api_key: str = ""
    anthropic_model: str = "claude-haiku-4-5-20251001"

    cors_origins: str = "http://localhost:5173,https://fishing-daily.web.app,https://fishing-daily.firebaseapp.com"
    environment: str = "development"

    class Config:
        env_file = str(_ENV_FILE)
        env_file_encoding = "utf-8"

settings = Settings()
