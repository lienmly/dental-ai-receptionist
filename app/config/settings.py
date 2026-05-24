from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    llm_api_key: str
    llm_base_url: str = "https://api.deepseek.com"
    llm_model: str = "deepseek-v4-flash"

    google_calendar_id: str = ""
    google_service_account_file: str = "service-account.json"
    google_service_account_json: Optional[str] = None  # For Railway/cloud deploy

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()